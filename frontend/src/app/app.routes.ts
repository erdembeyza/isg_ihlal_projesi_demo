import { Routes } from '@angular/router';
import { adminGuard } from './core/guards/admin.guard';
import { foremanGuard } from './core/guards/foreman.guard';

export const routes: Routes = [
  { path: 'giris', loadComponent: () => import('./features/login/login').then((m) => m.Login) },
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
  { path: '', pathMatch: 'full', redirectTo: 'giris' },
  { path: '**', redirectTo: 'giris' },
];
