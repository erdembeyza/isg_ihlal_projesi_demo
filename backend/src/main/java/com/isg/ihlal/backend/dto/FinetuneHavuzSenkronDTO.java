package com.isg.ihlal.backend.dto;

/**
 * MODUL-6: HATALI_TESPIT kayitlarinin fine-tune havuzuna senkron sonucu.
 */
public record FinetuneHavuzSenkronDTO(int toplam, int kopyalanan, int atlanan, int hata) {
}
