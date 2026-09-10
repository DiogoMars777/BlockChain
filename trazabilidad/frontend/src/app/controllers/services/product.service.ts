import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import {
  Product,
  ProductCreate,
  ProductUpdate,
  ProductListResponse,
  Variant,
  VariantCreate,
  VariantUpdate
} from '../../models/auth.models';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ProductService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/products`;
  private variantUrl = `${environment.apiUrl}/variants`;

  productsSignal = signal<Product[]>([]);
  totalProductsSignal = signal<number>(0);
  isLoadingSignal = signal<boolean>(false);
  selectedProductSignal = signal<Product | null>(null);

  getProducts(search: string = '', idcategoria?: number, skip: number = 0, limit: number = 50): Observable<ProductListResponse> {
    this.isLoadingSignal.set(true);
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    if (search.trim()) params = params.set('search', search.trim());
    if (idcategoria) params = params.set('idcategoria', idcategoria.toString());

    return this.http.get<ProductListResponse>(this.apiUrl, { params }).pipe(
      tap((res) => {
        this.productsSignal.set(res.items);
        this.totalProductsSignal.set(res.total);
        this.isLoadingSignal.set(false);
      })
    );
  }

  getProductById(idproducto: number): Observable<Product> {
    return this.http.get<Product>(`${this.apiUrl}/${idproducto}`).pipe(
      tap((prod) => this.selectedProductSignal.set(prod))
    );
  }

  createProduct(data: ProductCreate): Observable<Product> {
    return this.http.post<Product>(this.apiUrl, data);
  }

  updateProduct(idproducto: number, data: ProductUpdate): Observable<Product> {
    return this.http.put<Product>(`${this.apiUrl}/${idproducto}`, data);
  }

  deleteProduct(idproducto: number): Observable<Product> {
    return this.http.delete<Product>(`${this.apiUrl}/${idproducto}`);
  }

  // Variantes
  addVariant(idproducto: number, data: VariantCreate): Observable<Variant> {
    return this.http.post<Variant>(`${this.apiUrl}/${idproducto}/variants`, data);
  }

  updateVariant(idvariante: number, data: VariantUpdate): Observable<Variant> {
    return this.http.put<Variant>(`${this.variantUrl}/${idvariante}`, data);
  }

  deleteVariant(idvariante: number): Observable<{ detail: string }> {
    return this.http.delete<{ detail: string }>(`${this.variantUrl}/${idvariante}`);
  }
}
