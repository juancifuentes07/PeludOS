import { Routes } from '@angular/router';

import { authGuard } from './core/auth.guard';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('./pages/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'registro',
    loadComponent: () => import('./pages/registro/registro.component').then((m) => m.RegistroComponent),
  },
  {
    path: '',
    canActivate: [authGuard],
    loadComponent: () => import('./pages/layout/layout.component').then((m) => m.LayoutComponent),
    children: [
      {
        path: 'inicio',
        loadComponent: () => import('./pages/inicio/inicio.component').then((m) => m.InicioComponent),
      },
      {
        path: 'mascotas',
        loadComponent: () => import('./pages/mascotas/mascotas.component').then((m) => m.MascotasComponent),
      },
      {
        path: 'veterinarias',
        loadComponent: () =>
          import('./pages/veterinarias/veterinarias.component').then((m) => m.VeterinariasComponent),
      },
      {
        path: 'citas',
        loadComponent: () => import('./pages/citas/citas.component').then((m) => m.CitasComponent),
      },
      { path: '', pathMatch: 'full', redirectTo: 'inicio' },
    ],
  },
  { path: '**', redirectTo: 'inicio' },
];