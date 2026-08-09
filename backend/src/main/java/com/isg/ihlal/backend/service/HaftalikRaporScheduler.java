package com.isg.ihlal.backend.service;

import com.isg.ihlal.backend.dto.HaftalikRaporOzetDTO;
import com.isg.ihlal.backend.security.AuthenticatedUser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.util.List;

/**
 * Her Pazartesi 08:00'de onceki 7 gunun ozetini Telegram'a gonderir.
 */
@Component
public class HaftalikRaporScheduler {

    private static final Logger log = LoggerFactory.getLogger(HaftalikRaporScheduler.class);

    private final RaporService raporService;
    private final TelegramBildirimService telegramBildirimService;
    private final String publicBaseUrl;

    public HaftalikRaporScheduler(
            RaporService raporService,
            TelegramBildirimService telegramBildirimService,
            @Value("${app.public-base-url:http://localhost:8080}") String publicBaseUrl
    ) {
        this.raporService = raporService;
        this.telegramBildirimService = telegramBildirimService;
        this.publicBaseUrl = publicBaseUrl;
    }

    @Scheduled(cron = "0 0 8 * * MON")
    public void haftalikRaporGonder() {
        LocalDate bitis = LocalDate.now().minusDays(1);
        LocalDate baslangic = bitis.minusDays(6);

        // Cron sistem kullanicisi: tum fabrika kapsami (bolge filtresi yok)
        AuthenticatedUser sistem = new AuthenticatedUser(0L, "sistem", "ISG_YONETICI", null, List.of());
        HaftalikRaporOzetDTO ozet = raporService.ozet(sistem, baslangic, bitis);

        String mesaj = """
                📊 Haftalik ISG raporu (%s - %s)
                Toplam: %d | Aktif: %d | Cozuldu: %d | Hatali: %d
                PDF: %s/api/raporlar/haftalik.pdf?baslangic=%s&bitis=%s
                (PDF indirmek icin yonetici oturumu gerekir)
                """.formatted(
                ozet.baslangic(),
                ozet.bitis(),
                ozet.toplamIhlal(),
                ozet.aktif(),
                ozet.cozuldu(),
                ozet.hataliTespit(),
                publicBaseUrl,
                baslangic,
                bitis
        );

        log.info("Haftalik rapor cron calisti: toplam={}", ozet.toplamIhlal());
        telegramBildirimService.metinGonder(mesaj);
    }
}
