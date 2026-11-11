import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { API_URL } from '../../core/api.config';

interface Usuario {
  id_usuario: number;
  nombre_completo: string;
  correo_electronico: string;
  rol: string;
}

@Component({
  selector: 'app-inicio',
  imports: [RouterLink],
  template: `
    <main class="contenedor">
      @if (usuario(); as u) {
        <section class="tarjeta">
          <h1>Hola, {{ u.nombre_completo }}</h1>
          <p class="texto-suave">{{ u.correo_electronico }}</p>
          <div class="acciones">
            <a class="btn btn-primario" routerLink="/mascotas">Ver mis mascotas</a>
          </div>
        </section>
      } @else {
        <p class="texto-suave">Cargando...</p>
      }
    </main>
  `,
})
export class InicioComponent implements OnInit {
  private http = inject(HttpClient);

  usuario = signal<Usuario | null>(null);

  ngOnInit() {
    this.http.get<Usuario>(`${API_URL}/usuarios/me`).subscribe((u) => this.usuario.set(u));
  }
}