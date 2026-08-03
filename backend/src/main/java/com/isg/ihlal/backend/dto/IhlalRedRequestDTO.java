package com.isg.ihlal.backend.dto;

/**
 * DTO-6 (tasarim_mimari.md): POST /api/ihlaller/{id}/reddet govdesi.
 * ihlalId alani dokumantasyonda yer alir; asil kimlik zaten path
 * degiskeninden ({id}) alinir, bu alan sadece istemci tarafinda cift
 * kontrol/loglama amaciyla opsiyonel olarak gonderilebilir.
 */
public record IhlalRedRequestDTO(
        Long ihlalId,
        String redNedeni
) {
}
