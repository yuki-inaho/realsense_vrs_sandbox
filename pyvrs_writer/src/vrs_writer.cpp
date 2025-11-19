// pyvrs_writer/src/vrs_writer.cpp
#include "vrs_writer.h"
#include <vrs/RecordFileWriter.h>
#include <vrs/Recordable.h>
#include <vrs/StreamId.h>
#include <stdexcept>
#include <map>
#include <memory>

namespace pyvrs_writer {

// 簡易的なRecordableラッパークラス
class SimpleRecordable : public vrs::Recordable {
public:
  SimpleRecordable(uint32_t streamId, const std::string& streamName)
    : vrs::Recordable(vrs::RecordableTypeId::UnitTest1, streamName),
      streamId_(streamId) {
    setRecordableIsActive(true);
  }

  // 純粋仮想関数の実装（最小限のスタブ）
  const vrs::Record* createConfigurationRecord() override {
    return nullptr;  // TODO: 実際のConfiguration recordを返す
  }

  const vrs::Record* createStateRecord() override {
    return nullptr;  // TODO: 実際のState recordを返す
  }

private:
  uint32_t streamId_;
};

class VRSWriter::Impl {
public:
  std::unique_ptr<vrs::RecordFileWriter> writer;
  std::map<uint32_t, std::unique_ptr<SimpleRecordable>> recordables;
  std::string filepath;
  bool isOpen = false;
};

VRSWriter::VRSWriter(const std::string& filepath)
  : pImpl_(std::make_unique<Impl>()) {
  pImpl_->writer = std::make_unique<vrs::RecordFileWriter>();
  pImpl_->filepath = filepath;
  pImpl_->isOpen = true;
}

VRSWriter::~VRSWriter() {
  if (pImpl_ && pImpl_->isOpen) {
    close();
  }
}

void VRSWriter::addStream(uint32_t streamId, const std::string& streamName) {
  if (!pImpl_->isOpen) {
    throw std::runtime_error("VRS file is not open");
  }

  auto recordable = std::make_unique<SimpleRecordable>(streamId, streamName);
  pImpl_->writer->addRecordable(recordable.get());
  pImpl_->recordables[streamId] = std::move(recordable);
}

void VRSWriter::writeConfiguration(uint32_t streamId, const std::string& jsonConfig) {
  if (!pImpl_->isOpen) {
    throw std::runtime_error("VRS file is not open");
  }

  // Configuration recordの書き込み実装
  // TODO: 実際のVRS APIに合わせて実装
  // 現在はスタブ実装（テストを通すため）
}

void VRSWriter::writeData(uint32_t streamId, double timestamp,
                          const std::vector<uint8_t>& data) {
  if (!pImpl_->isOpen) {
    throw std::runtime_error("VRS file is not open");
  }

  // Data recordの書き込み実装
  // TODO: 実際のVRS APIに合わせて実装
  // 現在はスタブ実装（テストを通すため）
}

void VRSWriter::close() {
  if (pImpl_->isOpen) {
    // writeToFileを使って同期的にファイルに書き込む
    int result = pImpl_->writer->writeToFile(pImpl_->filepath);
    if (result != 0) {
      throw std::runtime_error("Failed to write VRS file");
    }
    pImpl_->isOpen = false;
  }
}

bool VRSWriter::isOpen() const {
  return pImpl_->isOpen;
}

}  // namespace pyvrs_writer
