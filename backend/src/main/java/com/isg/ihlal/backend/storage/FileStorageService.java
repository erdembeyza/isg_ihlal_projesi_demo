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
import java.nio.file.StandardCopyOption;
import java.util.Base64;
import java.util.Locale;
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
    private static final String FINETUNE_HAVUZ = "finetune-havuz";

    private final Path uploadKok;
    private final Path kokDizin;
    private final Path finetuneHavuz;

    public FileStorageService(@Value("${app.upload-dir}") String uploadDir) {
        this.uploadKok = Paths.get(uploadDir).toAbsolutePath().normalize();
        this.kokDizin = uploadKok.resolve(ALT_KLASOR).normalize();
        this.finetuneHavuz = uploadKok.resolve(FINETUNE_HAVUZ).normalize();
    }

    @PostConstruct
    public void klasoruHazirla() {
        try {
            Files.createDirectories(kokDizin);
            Files.createDirectories(finetuneHavuz);
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

    /**
     * MODUL-6: reddedilen (HATALI_TESPIT) ihlalin orijinal kanitini
     * fine-tune havuzuna kopyalar. Hedef zaten varsa true doner (idempotent).
     *
     * @return true kopyalandi veya zaten vardı; false kaynak dosya yoksa
     */
    public boolean finetuneHavuzunaKopyala(String orijinalFotoUrl, Long ihlalId, String ihlalTipiAdi) {
        if (!StringUtils.hasText(orijinalFotoUrl) || ihlalId == null) {
            return false;
        }

        Path kaynak = urlDenDosyaYolu(orijinalFotoUrl);
        if (!Files.isRegularFile(kaynak)) {
            return false;
        }

        String tipKlasoru = guvenliKlasorAdi(ihlalTipiAdi);
        Path hedefKlasor = finetuneHavuz.resolve(tipKlasoru);
        try {
            Files.createDirectories(hedefKlasor);
            Path hedef = hedefKlasor.resolve(ihlalId + "_orijinal.jpg");
            if (Files.exists(hedef)) {
                return true;
            }
            Files.copy(kaynak, hedef, StandardCopyOption.COPY_ATTRIBUTES);
            return true;
        } catch (IOException e) {
            throw new ResponseStatusException(
                    INTERNAL_SERVER_ERROR,
                    "Fine-tune havuzuna kopyalanamadi: ihlalId=" + ihlalId,
                    e
            );
        }
    }

    public Path getKokDizin() {
        return kokDizin;
    }

    public Path getFinetuneHavuz() {
        return finetuneHavuz;
    }

    private Path urlDenDosyaYolu(String fotoUrl) {
        String temiz = fotoUrl.startsWith("/uploads/")
                ? fotoUrl.substring("/uploads/".length())
                : fotoUrl.replaceFirst("^/+", "");
        Path yol = uploadKok.resolve(temiz).normalize();
        if (!yol.startsWith(uploadKok)) {
            throw new ResponseStatusException(
                    org.springframework.http.HttpStatus.BAD_REQUEST,
                    "Gecersiz foto yolu"
            );
        }
        return yol;
    }

    private static String guvenliKlasorAdi(String ihlalTipiAdi) {
        if (!StringUtils.hasText(ihlalTipiAdi)) {
            return "BILINMEYEN";
        }
        String temiz = ihlalTipiAdi.trim().toUpperCase(Locale.ROOT)
                .replaceAll("[^A-Z0-9_-]", "_");
        return temiz.isEmpty() ? "BILINMEYEN" : temiz;
    }
}
