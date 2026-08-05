package com.isg.ihlal.backend.service;

import com.isg.ihlal.backend.entity.Ihlal;
import com.isg.ihlal.backend.util.SureFormatUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.util.Map;

@Service
public class TelegramBildirimService {

    private static final Logger log = LoggerFactory.getLogger(TelegramBildirimService.class);

    private final boolean enabled;
    private final String botToken;
    private final String chatId;
    private final RestClient restClient;

    public TelegramBildirimService(
            @Value("${app.telegram.enabled:false}") boolean enabled,
            @Value("${app.telegram.bot-token:}") String botToken,
            @Value("${app.telegram.chat-id:}") String chatId
    ) {
        this.enabled = enabled;
        this.botToken = botToken == null ? "" : botToken.trim();
        this.chatId = chatId == null ? "" : chatId.trim();
        this.restClient = RestClient.create();
    }

    @Async
    public void yeniIhlalBildir(Ihlal ihlal) {
        if (!yapilandirilmisMi()) {
            log.debug("Telegram kapali/yapilandirilmamis — ihlal bildirimi atlandi id={}", ihlal.getId());
            return;
        }

        String sure = SureFormatUtil.metin(ihlal.getSureSaniye());
        String mesaj = """
                🚨 Yeni ISG ihlali
                Bölge: %s
                Tip: %s
                Süre: %s
                Zaman: %s
                ID: %d
                """.formatted(
                ihlal.getBolge().getBolgeAdi(),
                ihlal.getIhlalTipi().getTipAdi(),
                sure,
                ihlal.getTespitZamani(),
                ihlal.getId()
        );
        mesajGonder(mesaj);
    }

    @Async
    public void metinGonder(String mesaj) {
        if (!yapilandirilmisMi()) {
            log.info("Telegram kapali — mesaj: {}", mesaj);
            return;
        }
        mesajGonder(mesaj);
    }

    private void mesajGonder(String mesaj) {
        try {
            String url = "https://api.telegram.org/bot" + botToken + "/sendMessage";
            restClient.post()
                    .uri(url)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(Map.of(
                            "chat_id", chatId,
                            "text", mesaj,
                            "disable_web_page_preview", true
                    ))
                    .retrieve()
                    .toBodilessEntity();
        } catch (Exception ex) {
            log.warn("Telegram bildirimi gonderilemedi: {}", ex.getMessage());
        }
    }

    private boolean yapilandirilmisMi() {
        return enabled && !botToken.isBlank() && !chatId.isBlank();
    }
}
