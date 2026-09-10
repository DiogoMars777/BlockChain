import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CategoryService } from '../services/category.service';
import { Category, CategoryCreate, CategoryUpdate } from '../../models/auth.models';

@Component({
  selector: 'app-category-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: '../../views/pages/category-management.view.html',
  styleUrls: ['../../views/pages/category-management.view.css']
})
export class CategoryManagementController implements OnInit {
  private categoryService = inject(CategoryService);
  private router = inject(Router);

  categories = this.categoryService.categoriesSignal;
  isLoading = this.categoryService.isLoadingSignal;

  isModalOpen = signal<boolean>(false);
  editingCategory = signal<Category | null>(null);

  // Campos del formulario
  nombrecategoria = signal<string>('');
  descripcion = signal<string>('');

  errorMessage = signal<string>('');
  successMessage = signal<string>('');

  ngOnInit() {
    this.loadCategories();
  }

  loadCategories() {
    this.categoryService.getCategories().subscribe({
      error: () => this.errorMessage.set('Error al cargar las categorías.')
    });
  }

  openCreateModal() {
    this.editingCategory.set(null);
    this.nombrecategoria.set('');
    this.descripcion.set('');
    this.errorMessage.set('');
    this.isModalOpen.set(true);
  }

  openEditModal(cat: Category) {
    this.editingCategory.set(cat);
    this.nombrecategoria.set(cat.nombrecategoria);
    this.descripcion.set(cat.descripcion || '');
    this.errorMessage.set('');
    this.isModalOpen.set(true);
  }

  closeModal() {
    this.isModalOpen.set(false);
  }

  saveCategory() {
    if (!this.nombrecategoria().trim()) {
      this.errorMessage.set('El nombre de la categoría es obligatorio.');
      return;
    }

    const currentEdit = this.editingCategory();
    if (currentEdit) {
      const updateData: CategoryUpdate = {
        nombrecategoria: this.nombrecategoria().trim(),
        descripcion: this.descripcion().trim() || undefined
      };
      this.categoryService.updateCategory(currentEdit.idcategoria, updateData).subscribe({
        next: () => {
          this.successMessage.set('Categoría actualizada con éxito.');
          this.closeModal();
          setTimeout(() => this.successMessage.set(''), 3000);
        },
        error: (err) => this.errorMessage.set(err.error?.detail || 'Error al actualizar categoría.')
      });
    } else {
      const createData: CategoryCreate = {
        nombrecategoria: this.nombrecategoria().trim(),
        descripcion: this.descripcion().trim() || undefined
      };
      this.categoryService.createCategory(createData).subscribe({
        next: () => {
          this.successMessage.set('Categoría creada con éxito.');
          this.closeModal();
          setTimeout(() => this.successMessage.set(''), 3000);
        },
        error: (err) => this.errorMessage.set(err.error?.detail || 'Error al crear categoría.')
      });
    }
  }

  deleteCategory(cat: Category) {
    if (confirm(`¿Estás seguro de eliminar la categoría "${cat.nombrecategoria}"?`)) {
      this.categoryService.deleteCategory(cat.idcategoria).subscribe({
        next: () => {
          this.successMessage.set('Categoría eliminada.');
          setTimeout(() => this.successMessage.set(''), 3000);
        },
        error: (err) => alert(err.error?.detail || 'Error al eliminar la categoría.')
      });
    }
  }

  navigateToDashboard() {
    this.router.navigate(['/dashboard']);
  }
}
