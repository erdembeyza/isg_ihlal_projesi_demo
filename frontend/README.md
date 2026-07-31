# Frontend (Angular)

Bu klasör, Angular tabanlı web arayüzünü (Login, Admin/Formen Dashboard,
İhlal Listesi, İstatistik Grafiği, İhlal Detay Modalı) barındıracaktır.

Angular projesi **Faz 5-6** kapsamında Angular CLI ile bu klasör içinde
oluşturulacaktır:

```powershell
ng new frontend --directory . --routing --style scss
```

**Planlanan bileşen hiyerarşisi** (`tasarim_mimari.md` — BİLEŞENLER bölümü):

- `LoginComponent`
- `AdminDashboardComponent`
  - `IhlalListesiComponent`
  - `IstatistikGrafikComponent`
  - `IhlalDetayModalComponent`
- `ForemanDashboardComponent`
  - `IhlalListesiComponent`
  - `IstatistikGrafikComponent`
