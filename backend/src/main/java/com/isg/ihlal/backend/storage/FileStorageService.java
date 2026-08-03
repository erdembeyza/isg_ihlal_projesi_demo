package com.isg.ihlal.backend.storage;

import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.server.ResponseStatusException;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Base64;
import java.util.UUID;

import static org.springframework.http.HttpStatus.INTERNAL_SERVER_ERROR;

/**
 * MODUL-2 (tasarim_mimari.md): "Kanit gorsellerini (orijinal/blurlu) dosya
 * sistemine/nesne depolamaya yazar, veritabanina yalnizca dosya yolunu isler".
 * <p>
 * Gelistirme ortaminda yerel dosya sistemine yazar; ileride S3/nesne depolama
 * gibi bir alternatife gecilirse yalnizca bu servisin degismesi yeterlidir.
 */
@Service
public class FileStorageService {

    private static final String ALT_KLASOR = "ihlaller";

    private final Path kokDizin;

    public FileStorageService(@Value("${app.upload-dir}") String uploadDir) {
        this.kokDizin = Paths.get(uploadDir, ALT_KLASOR).toAbsolutePath().normalize();
    }

    @PostConstruct
    public void klasoruHazirla() {
        try {
            Files.createDirectories(kokDizin);
        } catch (IOException e) {
            throw new ResponseStatusException(INTERNAL_SERVER_ERROR, "Yukleme klasoru olusturulamadi", e);
        }
    }

    /**
     * Base64 kodlu bir goruntuyu diske yazar ve statik olarak erisilebilecegi
     * bagil URL'i ("/uploads/ihlaller/...") doner (bkz. WebConfig).
     *
     * @param base64Icerik "data:image/jpeg;base64,..." on eki olsun ya da olmasin kabul edilir.
     * @param dosyaOnEki   dosya adina okunabilirlik icin eklenen etiket (ör. "orijinal", "blur")
     */
    public String base64FotoKaydet(String base64Icerik, String dosyaOnEki) {
        String temizIcerik = base64Icerik;
        int virgulIndex = base64Icerik.indexOf(',');
        if (base64Icerik.startsWith("data:") && virgulIndex >= 0) {
            temizIcerik = base64Icerik.substring(virgulIndex + 1);
        }

        byte[] veri;
        try {
            veri = Base64.getDecoder().decode(temizIcerik);
        } catch (IllegalArgumentException e) {
            throw new ResponseStatusException(
                    org.springframework.http.HttpStatus.BAD_REQUEST,
                    "Gecersiz base64 foto icerigi: " + dosyaOnEki
            );
        }

        String dosyaAdi = UUID.randomUUID() + "_" + StringUtils.trimAllWhitespace(dosyaOnEki) + ".jpg";
        Path hedefYol = kokDizin.resolve(dosyaAdi);

        try {
            Files.write(hedefYol, veri);
        } catch (IOException e) {
            throw new ResponseStatusException(INTERNAL_SERVER_ERROR, "Foto diske yazilamadi", e);
        }

        return "/uploads/" + ALT_KLASOR + "/" + dosyaAdi;
    }

    public Path getKokDizin() {
        return kokDizin;
    }
}
