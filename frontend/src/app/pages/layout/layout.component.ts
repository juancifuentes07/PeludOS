import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-layout',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <header class="topbar">
      <div class="topbar-izq">
        <span class="marca">PeludOS</span>
        <nav class="nav">
          <a routerLink="/inicio" routerLinkActive="activo">Inicio</a>
          <a routerLink="/mascotas" routerLinkActive="activo">Mascotas</a>
          <a routerLink="/veterinarias" routerLinkActive="activo">Veterinarias</a>
          <a routerLink="/citas" routerLinkActive="activo">Citas</a>
        </nav>
      </div>
      <button class="btn btn-fantasma" type="button" (click)="auth.logout()">Cerrar sesión</button>
    </header>
    <router-outlet />
  `,
})
export class LayoutComponent {
  auth = inject(AuthService);
}