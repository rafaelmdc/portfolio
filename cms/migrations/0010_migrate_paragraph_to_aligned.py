import json
from django.db import migrations


def _convert_forward(blocks):
    changed = False
    for block in blocks:
        btype = block.get('type')
        bvalue = block.get('value')
        if btype == 'paragraph' and isinstance(bvalue, str):
            block['value'] = {'text': bvalue, 'alignment': 'justify'}
            changed = True
        elif btype == 'section' and isinstance(bvalue, dict):
            inner = bvalue.get('inner', [])
            if isinstance(inner, list) and _convert_forward(inner):
                changed = True
    return changed


def _convert_reverse(blocks):
    changed = False
    for block in blocks:
        btype = block.get('type')
        bvalue = block.get('value')
        if btype == 'paragraph' and isinstance(bvalue, dict) and 'text' in bvalue:
            block['value'] = bvalue['text']
            changed = True
        elif btype == 'section' and isinstance(bvalue, dict):
            inner = bvalue.get('inner', [])
            if isinstance(inner, list) and _convert_reverse(inner):
                changed = True
    return changed


def migrate_forward(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        for table in ('cms_blogpage', 'cms_portfolioprojectpage'):
            cursor.execute(f"SELECT id, body FROM {table}")  # noqa: S608
            for page_id, body in cursor.fetchall():
                if not body or not isinstance(body, list):
                    continue
                if _convert_forward(body):
                    cursor.execute(
                        f"UPDATE {table} SET body = %s::jsonb WHERE id = %s",  # noqa: S608
                        [json.dumps(body), page_id],
                    )


def migrate_reverse(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        for table in ('cms_blogpage', 'cms_portfolioprojectpage'):
            cursor.execute(f"SELECT id, body FROM {table}")  # noqa: S608
            for page_id, body in cursor.fetchall():
                if not body or not isinstance(body, list):
                    continue
                if _convert_reverse(body):
                    cursor.execute(
                        f"UPDATE {table} SET body = %s::jsonb WHERE id = %s",  # noqa: S608
                        [json.dumps(body), page_id],
                    )


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0009_alter_paragraph_block_to_aligned'),
    ]

    operations = [
        migrations.RunPython(migrate_forward, migrate_reverse),
    ]
