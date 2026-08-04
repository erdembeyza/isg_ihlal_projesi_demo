package com.isg.ihlal.backend.entity;

/**
 * kullanicilar.rol icin izin verilen degerler (bkz. ck_kullanici_rol CHECK kisiti).
 * AI_CORE_SERVIS: yalnizca AI Core'un POST /api/ihlaller cagrisi icin;
 * panel girisi / listeleme yetkisi yoktur.
 */
public enum Rol {
    ISG_YONETICI,
    FORMEN,
    AI_CORE_SERVIS
}
