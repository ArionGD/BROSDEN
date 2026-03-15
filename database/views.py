from django.shortcuts import render
from django.apps import apps
from accounts.decorators import admin_required

@admin_required
def database_schema(request):
    """Reflects on all installed models and their fields to show the database structure."""
    all_models = apps.get_models()
    db_schema = []
    
    # Sort models by app label for better organization
    all_models = sorted(all_models, key=lambda x: (x._meta.app_label, x._meta.object_name))

    for model in all_models:
        # We can exclude standard django apps if we want, but let's show everything 
        # as requested, maybe just highlighting main ones.
        
        db_schema.append({
            'app_label': model._meta.app_label,
            'model_name': model._meta.object_name,
            'table_name': model._meta.db_table,
            'fields': [
                {
                    'name': field.name,
                    'type': field.get_internal_type(),
                    'verbose_name': getattr(field, 'verbose_name', field.name).title(),
                    'help_text': field.help_text,
                }
                for field in model._meta.fields
            ],
            'row_count': model.objects.count() if not model._meta.abstract else 0
        })
    
    return render(request, 'database/database.html', {'schema': db_schema})
