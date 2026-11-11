import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule, RouterLink],
  template: `
    <main class="pagina-auth">
      <section class="tarjeta tarjeta-auth">
        <h1 class="marca-grande">PeludOS</h1>
        <p class="texto-suave">Cuidado de tus mascotas, en un solo lugar</p>

        <form class="formulario" [formGroup]="form" (ngSubmit)="enviar()">
          <label class="campo">
            Correo electrónico
            <input type="email" formControlName="correo" autocomplete="username" />
          </label>
          <label class="campo">
            Contraseña
            <input type="password" formControlName="contrasena" autocomplete="current-password" />
          </label>

          @if (error()) {
            <p class="alerta-error">{{ error() }}</p>
          }

          <button class="btn btn-primario" type="submit" [disabled]="form.invalid || cargando()">
            {{ cargando() ? 'Ingresando...' : 'Ingresar' }}
          </button>
        </form>

        <p class="enlace-auth">¿No tienes cuenta? <a routerLink="/registro">Regístrate</a></p>
      </section>
    </main>
  `,
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  private router = inject(Router);

  form = this.fb.nonNullable.group({
    correo: ['', [Validators.required, Validators.email]],
    contrasena: ['', Validators.required],
  });

  cargando = signal(false);
  error = signal<string | null>(null);

  enviar() {
    if (this.form.invalid) return;
    this.cargando.set(true);
    this.error.set(null);

    const { correo, contrasena } = this.form.getRawValue();
    this.auth.login(correo, contrasena).subscribe({
      next: () => this.router.navigate(['/inicio']),
      error: (err: HttpErrorResponse) => {
        this.cargando.set(false);
        if (err.status === 0) {
          this.error.set('No se pudo conectar con el servidor');
        } else if (err.status === 400 || err.status === 401) {
          this.error.set('Correo o contraseña incorrectos');
        } else {
          this.error.set('Ocurrió un error, intenta de nuevo');
        }
      },
    });
  }
}