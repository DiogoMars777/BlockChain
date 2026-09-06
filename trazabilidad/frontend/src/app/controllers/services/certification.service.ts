import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import {
  Certification,
  CertificationCreate,
  CertificationUpdate,
  ProductCertification,
  ProductCertificationAssign
} from '../../models/auth.models';

@Injectable({
  providedIn: 'root'
})
export class CertificationService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000/api/v1/certifications';
  private productUrl = 'http://localhost:8000/api/v1/products';

  certificationsSignal = signal<Certification[]>([]);
  isLoadingSignal = signal<boolean>(false);

  getCertifications(): Observable<Certification[]> {
    this.isLoadingSignal.set(true);
    return this.http.get<Certification[]>(this.apiUrl).pipe(
      tap((certs) => {
        this.certificationsSignal.set(certs);
        this.isLoadingSignal.set(false);
      })
    );
  }

  createCertification(data: CertificationCreate): Observable<Certification> {
    return this.http.post<Certification>(this.apiUrl, data).pipe(
      tap(() => this.getCertifications().subscribe())
    );
  }

  updateCertification(idcertificacion: number, data: CertificationUpdate): Observable<Certification> {
    return this.http.put<Certification>(`${this.apiUrl}/${idcertificacion}`, data).pipe(
      tap(() => this.getCertifications().subscribe())
    );
  }

  deleteCertification(idcertificacion: number): Observable<{ detail: string }> {
    return this.http.delete<{ detail: string }>(`${this.apiUrl}/${idcertificacion}`).pipe(
      tap(() => this.getCertifications().subscribe())
    );
  }

  // Product links
  getProductCertifications(idproducto: number): Observable<ProductCertification[]> {
    return this.http.get<ProductCertification[]>(`${this.productUrl}/${idproducto}/certifications`);
  }

  assignProductCertification(idproducto: number, data: ProductCertificationAssign): Observable<ProductCertification> {
    return this.http.post<ProductCertification>(`${this.productUrl}/${idproducto}/certifications`, data);
  }

  removeProductCertification(idproducto: number, idcertificacion: number): Observable<{ detail: string }> {
    return this.http.delete<{ detail: string }>(`${this.productUrl}/${idproducto}/certifications/${idcertificacion}`);
  }
}
