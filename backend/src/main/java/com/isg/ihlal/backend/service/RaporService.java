package com.isg.ihlal.backend.service;

import com.isg.ihlal.backend.dto.HaftalikRaporOzetDTO;
import com.isg.ihlal.backend.entity.Ihlal;
import com.isg.ihlal.backend.entity.IhlalDurumu;
import com.isg.ihlal.backend.entity.Rol;
import com.isg.ihlal.backend.repository.IhlalRepository;
import com.isg.ihlal.backend.security.AuthenticatedUser;
import com.lowagie.text.Document;
import com.lowagie.text.DocumentException;
import com.lowagie.text.Font;
import com.lowagie.text.FontFactory;
import com.lowagie.text.Paragraph;
import com.lowagie.text.Phrase;
import com.lowagie.text.pdf.PdfPCell;
import com.lowagie.text.pdf.PdfPTable;
import com.lowagie.text.pdf.PdfWriter;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.awt.Color;
import java.io.ByteArrayOutputStream;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

@Service
@Transactional(readOnly = true)
public class RaporService {

    private static final DateTimeFormatter TARIH = DateTimeFormatter.ofPattern("dd.MM.yyyy");

    private final IhlalRepository ihlalRepository;

    public RaporService(IhlalRepository ihlalRepository) {
        this.ihlalRepository = ihlalRepository;
    }

    public HaftalikRaporOzetDTO ozet(AuthenticatedUser user, LocalDate baslangic, LocalDate bitis) {
        LocalDateTime bas = (baslangic != null ? baslangic : LocalDate.now().minusDays(7))
                .atStartOfDay();
        LocalDateTime bit = (bitis != null ? bitis : LocalDate.now())
                .atTime(LocalTime.MAX);

        List<Ihlal> kayitlar = isFormen(user)
                ? ihlalRepository.findByBolgeIdAndTespitZamaniBetween(user.bolgeId(), bas, bit)
                : ihlalRepository.findByTespitZamaniBetween(bas, bit);

        int aktif = (int) kayitlar.stream().filter(i -> i.getDurum() == IhlalDurumu.AKTIF).count();
        int cozuldu = (int) kayitlar.stream().filter(i -> i.getDurum() == IhlalDurumu.COZULDU).count();
        int hatali = (int) kayitlar.stream().filter(i -> i.getDurum() == IhlalDurumu.HATALI_TESPIT).count();

        List<HaftalikRaporOzetDTO.BolgeOzet> bolgeler = kayitlar.stream()
                .collect(Collectors.groupingBy(i -> i.getBolge().getBolgeAdi(), Collectors.counting()))
                .entrySet().stream()
                .map(e -> new HaftalikRaporOzetDTO.BolgeOzet(e.getKey(), e.getValue().intValue()))
                .sorted(Comparator.comparingInt(HaftalikRaporOzetDTO.BolgeOzet::adet).reversed())
                .toList();

        List<HaftalikRaporOzetDTO.TipOzet> tipler = kayitlar.stream()
                .collect(Collectors.groupingBy(i -> i.getIhlalTipi().getTipAdi(), Collectors.counting()))
                .entrySet().stream()
                .map(e -> new HaftalikRaporOzetDTO.TipOzet(e.getKey(), e.getValue().intValue()))
                .sorted(Comparator.comparingInt(HaftalikRaporOzetDTO.TipOzet::adet).reversed())
                .toList();

        Map<Integer, Long> saatSayim = kayitlar.stream()
                .collect(Collectors.groupingBy(i -> i.getTespitZamani().getHour(), Collectors.counting()));

        List<HaftalikRaporOzetDTO.SaatOzet> riskliSaatler = IntStream.range(0, 24)
                .mapToObj(saat -> new HaftalikRaporOzetDTO.SaatOzet(saat, saatSayim.getOrDefault(saat, 0L).intValue()))
                .filter(s -> s.adet() > 0)
                .sorted(Comparator.comparingInt(HaftalikRaporOzetDTO.SaatOzet::adet).reversed())
                .limit(8)
                .toList();

        return new HaftalikRaporOzetDTO(
                bas.toLocalDate().format(TARIH),
                bit.toLocalDate().format(TARIH),
                kayitlar.size(),
                aktif,
                cozuldu,
                hatali,
                bolgeler,
                tipler,
                riskliSaatler
        );
    }

    public byte[] pdfOlustur(AuthenticatedUser user, LocalDate baslangic, LocalDate bitis) {
        HaftalikRaporOzetDTO ozet = ozet(user, baslangic, bitis);
        try (ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            Document document = new Document();
            PdfWriter.getInstance(document, baos);
            document.open();

            Font baslik = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 16);
            Font normal = FontFactory.getFont(FontFactory.HELVETICA, 11);
            Font kucukBold = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 12);

            document.add(new Paragraph("ISG Haftalik Ihlal Raporu", baslik));
            document.add(new Paragraph("Donem: " + ozet.baslangic() + " - " + ozet.bitis(), normal));
            document.add(new Paragraph(" "));
            document.add(new Paragraph(
                    "Toplam: " + ozet.toplamIhlal()
                            + " | Aktif: " + ozet.aktif()
                            + " | Cozuldu: " + ozet.cozuldu()
                            + " | Hatali tespit: " + ozet.hataliTespit(),
                    normal
            ));
            document.add(new Paragraph(" "));

            document.add(new Paragraph("Bolge ozeti", kucukBold));
            document.add(tablo(List.of("Bolge", "Adet"),
                    ozet.bolgeOzetleri().stream().map(b -> List.of(b.bolgeAdi(), String.valueOf(b.adet()))).toList()));

            document.add(new Paragraph(" "));
            document.add(new Paragraph("Ihlal tipi ozeti", kucukBold));
            document.add(tablo(List.of("Tip", "Adet"),
                    ozet.tipOzetleri().stream().map(t -> List.of(t.tipAdi(), String.valueOf(t.adet()))).toList()));

            document.add(new Paragraph(" "));
            document.add(new Paragraph("En riskli saatler", kucukBold));
            document.add(tablo(List.of("Saat", "Adet"),
                    ozet.riskliSaatler().stream()
                            .map(s -> List.of(String.format("%02d:00", s.saat()), String.valueOf(s.adet())))
                            .toList()));

            document.close();
            return baos.toByteArray();
        } catch (Exception ex) {
            throw new IllegalStateException("PDF olusturulamadi: " + ex.getMessage(), ex);
        }
    }

    private PdfPTable tablo(List<String> basliklar, List<List<String>> satirlar) throws DocumentException {
        PdfPTable table = new PdfPTable(basliklar.size());
        table.setWidthPercentage(100);
        for (String h : basliklar) {
            PdfPCell cell = new PdfPCell(new Phrase(h));
            cell.setBackgroundColor(new Color(200, 200, 200));
            table.addCell(cell);
        }
        if (satirlar.isEmpty()) {
            PdfPCell bos = new PdfPCell(new Phrase("Kayit yok"));
            bos.setColspan(basliklar.size());
            table.addCell(bos);
        } else {
            for (List<String> satir : satirlar) {
                for (String hucre : satir) {
                    table.addCell(hucre);
                }
            }
        }
        return table;
    }

    private boolean isFormen(AuthenticatedUser user) {
        return user != null && Rol.FORMEN.name().equals(user.rol());
    }
}
