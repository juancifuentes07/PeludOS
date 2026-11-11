import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { AbstractControl, FormBuilder, ReactiveFormsModule, ValidationErrors, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { switchMap } from 'rxjs';

import { API_URL } from '../../core/api.config';
import { AuthService } from '../../core/auth.service';
import { mensajeDeError, vacioANull } from '../../core/utils';

function contrasenasCoinciden(grupo: AbstractControl): ValidationErrors | null {
  const a = grupo.get('contrasena')?.value;
  const b = grupo.get('confirmar')?.value;
  return a === b ? null : { noCoinciden: true };
}

@Component({
  selector: 'app-registro',
  imports: [ReactiveFormsModule, RouterLink],
  template: `
    <main class="pagina-auth">
      <section class="tarjeta tarjeta-auth tarjeta-auth-ancha">
        <h1 class="marca-grande">Crear cuenta</h1>
        <p class="texto-suave">Regístrate para empezar a cuidar a tus mascotas</p>

        <form class="formulario" [formGroup]="form" (ngSubmit)="enviar()">
          <label class="campo">
            Nombre completo *
            <input type="text" formControlName="nombre_completo" autocomplete="name" />
          </label>
          <label class="campo">
            Correo electrónico *
            <input type="email" formControlName="correo_electronico" autocomplete="email" />
          </label>
          <div class="fila-campos">
            <label class="campo">
              Contraseña * (mínimo 8 caracteres)
              <input type="password" formControlName="contrasena" autocomplete="new-password" />
            </label>
            <label class="campo">
              Confirmar contraseña *
              <input type="password" formControlName="confirmar" autocomplete="new-password" />
            </label>
          </div>
          @if (form.hasError('noCoinciden') && form.controls.confirmar.dirty) {
            <p class="alerta-error">Las contraseñas no coinciden</p>
          }
          <label class="campo">
            Teléfono
            <input type="tel" formControlName="telefono" autocomplete="tel" />
          </label>
          <label class="campo">
            Dirección
            <textarea formControlName="direccion" rows="2" autocomplete="street-address"></textarea>
          </label>

          @if (error()) {
            <p class="alerta-error">{{ error() }}</p>
          }

          <button class="btn btn-primario" type="submit" [disabled]="form.invalid || cargando()">
            {{ cargando() ? 'Creando cuenta...' : 'Crear cuenta' }}
          </button>
        </form>

        <p class="enlace-auth">¿Ya tienes cuenta? <a routerLink="/login">Ingresa</a></p>
      </section>
    </main>
  `,
})
export class RegistroComponent {
  private fb = inject(FormBuilder);
  private http = inject(HttpClient);
  private auth = inject(AuthService);
  private router = inject(Router);

  form = this.fb.nonNullable.group(
    {
      nombre_completo: ['', [Validators.required, Validators.maxLength(100), Validators.pattern(/\S/)]],
      correo_electronico: ['', [Validators.required, Validators.email, Validators.maxLength(100)]],
      contrasena: ['', [Validators.required, Validators.minLength(8)]],
      confirmar: ['', Validators.required],
      telefono: ['', Validators.maxLength(20)],
      direccion: [''],
    },
    { validators: [contrasenasCoinciden] },
  );

  cargando = signal(false);
  error = signal<string | null>(null);

  enviar() {
    if (this.form.invalid) return;
    this.cargando.set(true);
    this.error.set(null);

    const v = this.form.getRawValue();
    const correo = v.correo_electronico.trim();
    const datos = {
      nombre_completo: v.nombre_completo.trim(),
      correo_electronico: correo,
      contrasena: v.contrasena,
      telefono: vacioANull(v.telefono),
      direccion: vacioANull(v.direccion),
    };

    // Registra y, si sale bien, inicia sesión de una vez.
    this.http
      .post(`${API_URL}/auth/register`, datos)
      .pipe(switchMap(() => this.auth.login(correo, v.contrasena)))
      .subscribe({
        next: () => this.router.navigate(['/inicio']),
        error: (err: HttpErrorResponse) => {
          this.cargando.set(false);
          this.error.set(mensajeDeError(err));
        },
      });
  }
}