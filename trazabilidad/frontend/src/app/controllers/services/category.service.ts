import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { Category, CategoryCreate, CategoryUpdate } from '../../models/auth.models';

@Injectable({
  providedIn: 'root'
})
export class CategoryService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000/api/v1/categories';

  categoriesSignal = signal<Category[]>([]);
  isLoadingSignal = signal<boolean>(false);

  getCategories(): Observable<Category[]> {
    this.isLoadingSignal.set(true);
    return this.http.get<Category[]>(this.apiUrl).pipe(
      tap((categories) => {
        this.categoriesSignal.set(categories);
        this.isLoadingSignal.set(false);
      })
    );
  }

  createCategory(data: CategoryCreate): Observable<Category> {
    return this.http.post<Category>(this.apiUrl, data).pipe(
      tap(() => this.getCategories().subscribe())
    );
  }

  updateCategory(idcategoria: number, data: CategoryUpdate): Observable<Category> {
    return this.http.put<Category>(`${this.apiUrl}/${idcategoria}`, data).pipe(
      tap(() => this.getCategories().subscribe())
    );
  }

  deleteCategory(idcategoria: number): Observable<{ detail: string }> {
    return this.http.delete<{ detail: string }>(`${this.apiUrl}/${idcategoria}`).pipe(
      tap(() => this.getCategories().subscribe())
    );
  }
}
