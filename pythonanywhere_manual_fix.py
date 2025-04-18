#!/usr/bin/env python3
import os

def print_file_content(file_path):
    """Print the content of a file."""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return
    
    print(f"\n=== Content of {file_path} ===")
    with open(file_path, 'r', encoding='utf-8') as file:
        print(file.read())
    print(f"=== End of {file_path} ===\n")

def print_fixed_admin_dashboard():
    """Print a completely fixed admin_dashboard.html template."""
    print("\n=== FIXED admin_dashboard.html TEMPLATE ===")
    print("""{% extends 'base.html' %}

{% block title %}{{ _("Admin Dashboard") }}{% endblock %}

{% block content %}
<div class="container-fluid">
  <h1 class="mt-4">{{ _("Admin Dashboard") }}</h1>
  <div class="row">
    <div class="col-xl-3 col-md-6">
      <div class="card bg-primary text-white mb-4">
        <div class="card-body">
          <h5 class="card-title">{{ _("Total Products") }}</h5>
          <h2 class="display-4">{{ total_products }}</h2>
        </div>
        <div class="card-footer d-flex align-items-center justify-content-between">
          <a class="small text-white stretched-link" href="{{ url_for('view_products') }}">{{ _("View Products") }}</a>
          <div class="small text-white"><i class="fas fa-angle-right"></i></div>
        </div>
      </div>
    </div>
    <div class="col-xl-3 col-md-6">
      <div class="card bg-warning text-white mb-4">
        <div class="card-body">
          <h5 class="card-title">{{ _("Low Stock") }}</h5>
          <h2 class="display-4">{{ low_stock_count }}</h2>
        </div>
        <div class="card-footer d-flex align-items-center justify-content-between">
          <a class="small text-white stretched-link" href="#low-stock">{{ _("View Details") }}</a>
          <div class="small text-white"><i class="fas fa-angle-right"></i></div>
        </div>
      </div>
    </div>
    <div class="col-xl-3 col-md-6">
      <div class="card bg-success text-white mb-4">
        <div class="card-body">
          <h5 class="card-title">{{ _("Total Sales") }}</h5>
          <h2 class="display-4">{{ total_sales }}</h2>
        </div>
        <div class="card-footer d-flex align-items-center justify-content-between">
          <a class="small text-white stretched-link" href="{{ url_for('view_sales') }}">{{ _("View Sales") }}</a>
          <div class="small text-white"><i class="fas fa-angle-right"></i></div>
        </div>
      </div>
    </div>
    <div class="col-xl-3 col-md-6">
      <div class="card bg-danger text-white mb-4">
        <div class="card-body">
          <h5 class="card-title">{{ _("Total Revenue") }}</h5>
          <h2 class="display-4">{{ total_revenue }} RWF</h2>
        </div>
        <div class="card-footer d-flex align-items-center justify-content-between">
          <a class="small text-white stretched-link" href="{{ url_for('view_sales') }}">{{ _("View Revenue") }}</a>
          <div class="small text-white"><i class="fas fa-angle-right"></i></div>
        </div>
      </div>
    </div>
  </div>

  <div class="row">
    <div class="col-xl-6">
      <div class="card mb-4">
        <div class="card-header">
          <i class="fas fa-chart-bar mr-1"></i>
          {{ _("Monthly Sales") }}
        </div>
        <div class="card-body">
          <canvas id="monthlySalesChart" width="100%" height="40"></canvas>
        </div>
      </div>
    </div>
    <div class="col-xl-6">
      <div class="card mb-4">
        <div class="card-header">
          <i class="fas fa-chart-pie mr-1"></i>
          {{ _("Sales by Category") }}
        </div>
        <div class="card-body">
          <canvas id="categoryChart" width="100%" height="40"></canvas>
        </div>
      </div>
    </div>
  </div>

  <div class="row">
    <div class="col-xl-12">
      <div class="card mb-4" id="low-stock">
        <div class="card-header">
          <i class="fas fa-exclamation-triangle mr-1"></i>
          {{ _("Low Stock Products") }}
        </div>
        <div class="card-body">
          <h5 class="card-title">{{ _("Low Stock Products") }}</h5>
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>{{ _("Product Name") }}</th>
                  <th>{{ _("Category") }}</th>
                  <th>{{ _("Current Stock") }}</th>
                  <th>{{ _("Low Stock Threshold") }}</th>
                  <th>{{ _("Actions") }}</th>
                </tr>
              </thead>
              <tbody>
                {% if low_stock_products %}
                  {% for product in low_stock_products %}
                  <tr>
                    <td>{{ product.name }}</td>
                    <td>{{ product.category }}</td>
                    <td>{{ product.stock }}</td>
                    <td>{{ product.low_stock_threshold }}</td>
                    <td>
                      <a href="{{ url_for('edit_product', product_id=product.id) }}" class="btn btn-sm btn-primary">
                        <i class="fas fa-edit"></i> {{ _("Edit") }}
                      </a>
                    </td>
                  </tr>
                  {% endfor %}
                {% else %}
                  <tr><td colspan="5">{{ _("No low stock products") }}</td></tr>
                {% endif %}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
  document.addEventListener('DOMContentLoaded', function() {
    // Monthly Sales Chart
    var monthlySalesCtx = document.getElementById('monthlySalesChart').getContext('2d');
    var monthlySalesChart = new Chart(monthlySalesCtx, {
      type: 'bar',
      data: {
        labels: {{ monthly_labels|tojson }},
        datasets: [{
          label: '{{ _("Sales") }}',
          data: {{ monthly_data|tojson }},
          backgroundColor: 'rgba(54, 162, 235, 0.5)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });

    // Category Chart
    var categoryCtx = document.getElementById('categoryChart').getContext('2d');
    var categoryChart = new Chart(categoryCtx, {
      type: 'pie',
      data: {
        labels: {{ category_labels|tojson }},
        datasets: [{
          label: '{{ _("Sales by Category") }}',
          data: {{ category_data|tojson }},
          backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)',
            'rgba(255, 159, 64, 0.5)'
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)'
          ],
          borderWidth: 1
        }]
      }
    });
  });
</script>
{% endblock %}""")
    print("=== END OF FIXED TEMPLATE ===\n")

def print_fixed_view_sales():
    """Print a fixed view_sales.html template with delete button commented out."""
    print("\n=== INSTRUCTIONS FOR view_sales.html ===")
    print("Find the delete form that looks like this:")
    print("""<form action="{{ url_for('delete_sale', sale_id=sale.id) }}" method="POST" onsubmit="return confirm('{{ _('Are you sure you want to delete this sale? This will restore the stock to the product.') }}');">
  <button type="submit" class="btn btn-sm btn-danger">
    <i class="fas fa-trash"></i> {{ _("Delete") }}
  </button>
</form>""")
    print("\nAnd comment it out like this:")
    print("""<!--
<form action="{{ url_for('delete_sale', sale_id=sale.id) }}" method="POST" onsubmit="return confirm('{{ _('Are you sure you want to delete this sale? This will restore the stock to the product.') }}');">
  <button type="submit" class="btn btn-sm btn-danger">
    <i class="fas fa-trash"></i> {{ _("Delete") }}
  </button>
</form>
-->""")
    print("=== END OF INSTRUCTIONS ===\n")

if __name__ == "__main__":
    print("=== Smart Inventory System - PythonAnywhere Manual Fix Helper ===")
    
    # Print instructions for manual fixes
    print("\nThis script will help you manually fix the template issues.")
    print("Follow these steps:")
    
    print("\n1. First, check the current content of your templates:")
    print_file_content('templates/admin_dashboard.html')
    print_file_content('templates/view_sales.html')
    
    print("\n2. Now, replace the content of admin_dashboard.html with the fixed version:")
    print_fixed_admin_dashboard()
    
    print("\n3. For view_sales.html, follow these instructions:")
    print_fixed_view_sales()
    
    print("\n4. Finally, add the delete_sale route to app.py:")
    print("""
@app.route('/admin/sales/delete/<int:sale_id>', methods=['POST'])
@login_required
def delete_sale(sale_id):
    if not current_user.is_admin:
        flash(_('You do not have permission to delete sales.'), 'danger')
        return redirect(url_for('index'))
    
    sale = Sale.query.get_or_404(sale_id)
    
    # Restore the stock to the product
    product = Product.query.get(sale.product_id)
    if product:
        product.stock += sale.quantity
        db.session.add(product)
    
    db.session.delete(sale)
    db.session.commit()
    
    flash(_('Sale deleted successfully.'), 'success')
    return redirect(url_for('view_sales'))
""")
    
    print("\n=== After making these changes, reload your web application ===")
