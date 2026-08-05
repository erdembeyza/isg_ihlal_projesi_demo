import { Routes } from '@angular/router';
import { adminGuard } from './core/guards/admin.guard';
import { foremanGuard } from './core/guards/foreman.guard';
import { viewerGuard } from './core/guards/viewer.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./features/anasayfa/anasayfa').then((m) => m.Anasayfa),
  },
  {
    path: 'giris',
    loadComponent: () => import('./features/login/login').then((m) => m.Login),
  },
  {
    path: 'iletisim',
    loadComponent: () => import('./features/iletisim/iletisim').then((m) => m.Iletisim),
  },
  {
    path: 'uyelik-basvurusu',
    loadComponent: () =>
      import('./features/uyelik-basvurusu/uyelik-basvurusu').then((m) => m.UyelikBasvurusu),
  },
  {
    path: 'basvurularim',
    loadComponent: () =>
      import('./features/basvurularim/basvurularim').then((m) => m.Basvurularim),
  },
  {
    path: 'yonetici',
    loadComponent: () =>
      import('./features/admin-dashboard/admin-dashboard').then((m) => m.AdminDashboard),
    canActivate: [adminGuard],
  },
  {
    path: 'formen',
    loadComponent: () =>
      import('./features/foreman-dashboard/foreman-dashboard').then((m) => m.ForemanDashboard),
    canActivate: [foremanGuard],
  },
  {
    path: 'izleyici',
    loadComponent: () =>
      import('./features/viewer-dashboard/viewer-dashboard').then((m) => m.ViewerDashboard),
    canActivate: [viewerGuard],
  },
  { path: '**', redirectTo: '' },
];
