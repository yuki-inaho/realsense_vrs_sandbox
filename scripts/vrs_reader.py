"""VRS Reader module for reading VRS files.

This module provides a Pythonic interface to the PyVRS library,
which reads VRS (Virtual Reality Stream) files created by Meta.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

try:
    import pyvrs
except ImportError as e:
    raise ImportError(
        "pyvrs module not found. Please install with: uv add vrs"
    ) from e


class VRSReader:
    """VRS file reader with Pythonic interface and context manager support.

    This class wraps the pyvrs.SyncVRSReader to provide a simple interface
    for reading VRS files.

    Example:
        >>> with VRSReader("input.vrs") as reader:
        ...     stream_ids = reader.get_stream_ids()
        ...     config = reader.read_configuration(stream_ids[0])
        ...     for record in reader.read_data_records(stream_ids[0]):
        ...         print(record["timestamp"], record["data"])
    """

    def __init__(self, filepath: Path | str) -> None:
        """Initialize VRS reader and open VRS file.

        Args:
            filepath: Path to the VRS file to read (Path or str)

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If filepath is invalid or file is not a valid VRS file
            RuntimeError: If VRS file opening fails
        """
        if isinstance(filepath, str):
            filepath = Path(filepath)

        if not isinstance(filepath, Path):
            raise ValueError(
                f"filepath must be Path or str, got {type(filepath).__name__}"
            )

        if not filepath.exists():
            raise FileNotFoundError(f"VRS file not found: {filepath}")

        self._filepath = filepath
        self._reader: Any = None  # pyvrs.SyncVRSReader instance

        try:
            self._reader = pyvrs.SyncVRSReader(str(filepath))
        except Exception as e:
            raise RuntimeError(f"Failed to open VRS file '{filepath}': {e}") from e

    def __enter__(self) -> VRSReader:
        """Context manager entry.

        Returns:
            self
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Context manager exit. Automatically closes the file.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        self.close()

    def get_stream_ids(self) -> list[int]:
        """Get list of all stream IDs in the VRS file.

        Returns:
            List of stream IDs

        Raises:
            RuntimeError: If reader is not open
        """
        if self._reader is None:
            raise RuntimeError("VRS file is not open")

        try:
            # PyVRS stores stream IDs as strings, so we need to collect unique ones
            # by iterating through all records
            stream_ids_set: set[str] = set()
            for record in self._reader:
                stream_ids_set.add(record.stream_id)

            # Convert string stream IDs to integers
            # Stream ID format in PyVRS is like "1-1001" (RecordableTypeId-InstanceId)
            # We extract the numeric part after the dash
            numeric_ids = []
            for sid in stream_ids_set:
                try:
                    # Try to parse as "TypeId-InstanceId" format
                    if "-" in sid:
                        parts = sid.split("-")
                        numeric_ids.append(int(parts[-1]))
                    else:
                        # Try to parse as plain integer
                        numeric_ids.append(int(sid))
                except ValueError:
                    # If conversion fails, skip this stream ID
                    continue

            return sorted(numeric_ids)
        except Exception as e:
            raise RuntimeError(f"Failed to get stream IDs: {e}") from e

    def read_configuration(self, stream_id: int) -> dict[str, Any]:
        """Read configuration record for the specified stream.

        Args:
            stream_id: Target stream ID

        Returns:
            Configuration data as dictionary

        Raises:
            ValueError: If stream_id doesn't exist
            RuntimeError: If reader is not open or read fails
        """
        if self._reader is None:
            raise RuntimeError("VRS file is not open")

        if not isinstance(stream_id, int):
            raise ValueError(f"stream_id must be int, got {type(stream_id).__name__}")

        try:
            # Iterate through all records and find configuration for the stream
            for record in self._reader:
                # Match stream ID (convert record.stream_id to numeric for comparison)
                try:
                    if "-" in record.stream_id:
                        record_numeric_id = int(record.stream_id.split("-")[-1])
                    else:
                        record_numeric_id = int(record.stream_id)
                except (ValueError, AttributeError):
                    continue

                if (
                    record_numeric_id == stream_id
                    and record.record_type == pyvrs.RecordType.CONFIGURATION
                ):
                    # Get data from the record
                    data = record.get_data_bytes()
                    if data:
                        try:
                            # Try to decode as JSON
                            return json.loads(data.decode("utf-8"))
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            # Return as raw dict if not JSON
                            return {"data": data}

            # If no configuration found, raise error
            raise ValueError(f"No configuration record found for stream {stream_id}")
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(
                f"Failed to read configuration for stream {stream_id}: {e}"
            ) from e

    def read_data_records(self, stream_id: int) -> Iterator[dict[str, Any]]:
        """Read all data records for the specified stream.

        Args:
            stream_id: Target stream ID

        Yields:
            Dictionary with 'timestamp' and 'data' keys for each record

        Raises:
            ValueError: If stream_id doesn't exist
            RuntimeError: If reader is not open or read fails
        """
        if self._reader is None:
            raise RuntimeError("VRS file is not open")

        if not isinstance(stream_id, int):
            raise ValueError(f"stream_id must be int, got {type(stream_id).__name__}")

        try:
            for record in self._reader:
                # Match stream ID
                try:
                    if "-" in record.stream_id:
                        record_numeric_id = int(record.stream_id.split("-")[-1])
                    else:
                        record_numeric_id = int(record.stream_id)
                except (ValueError, AttributeError):
                    continue

                if record_numeric_id == stream_id and record.record_type == pyvrs.RecordType.DATA:
                    data = record.get_data_bytes()
                    if data is None:
                        data = b""

                    yield {
                        "timestamp": record.timestamp,
                        "data": data,
                    }
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(
                f"Failed to read data records for stream {stream_id}: {e}"
            ) from e

    def get_record_count(self, stream_id: int) -> int:
        """Get the number of data records for the specified stream.

        Args:
            stream_id: Target stream ID

        Returns:
            Number of data records

        Raises:
            ValueError: If stream_id doesn't exist
            RuntimeError: If reader is not open
        """
        if self._reader is None:
            raise RuntimeError("VRS file is not open")

        try:
            count = 0
            for record in self._reader:
                try:
                    if "-" in record.stream_id:
                        record_numeric_id = int(record.stream_id.split("-")[-1])
                    else:
                        record_numeric_id = int(record.stream_id)
                except (ValueError, AttributeError):
                    continue

                if record_numeric_id == stream_id and record.record_type == pyvrs.RecordType.DATA:
                    count += 1
            return count
        except Exception as e:
            raise RuntimeError(
                f"Failed to count records for stream {stream_id}: {e}"
            ) from e

    def close(self) -> None:
        """Close the VRS file.

        This method is called automatically when using the context manager.
        """
        if self._reader is not None:
            try:
                self._reader.close()
            except Exception:
                # Ignore close errors
                pass
            finally:
                self._reader = None
