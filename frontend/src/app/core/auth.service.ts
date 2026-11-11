import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { tap } from 'rxjs';

import { API_URL } from './api.config';

const TOKEN_KEY = 'peludos_token';

interface TokenResponse {
  access_token: string;
  token_type: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);

  private _token = signal<string | null>(localStorage.getItem(TOKEN_KEY));
  readonly isLoggedIn = computed(() => this._token() !== null);

  get token(): string | null {
    return this._token();
  }

  login(correo: string, contrasena: string) {
    // El login usa OAuth2PasswordRequestForm: form-urlencoded con 'username' y 'password'.
    // 'username' lleva el correo electrónico.
    const body = new HttpParams()
      .set('grant_type', 'password')
      .set('username', correo)
      .set('password', contrasena);

    return this.http.post<TokenResponse>(`${API_URL}/auth/login`, body).pipe(
      tap((res) => {
        localStorage.setItem(TOKEN_KEY, res.access_token);
        this._token.set(res.access_token);
      }),
    );
  }

  logout() {
    localStorage.removeItem(TOKEN_KEY);
    this._token.set(null);
    this.router.navigate(['/login']);
  }
}