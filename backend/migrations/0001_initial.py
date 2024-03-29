# Generated by Django 4.0.2 on 2022-02-14 14:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('status', models.CharField(choices=[('NA', 'Not Annotated'), ('WIP', 'Work In Progress'), ('C', 'Complete')], default='NA', max_length=3)),
            ],
            options={
                'verbose_name_plural': '   Datafiles',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('colour', models.CharField(max_length=64)),
            ],
            options={
                'verbose_name_plural': ' Tags',
            },
        ),
        migrations.CreateModel(
            name='TaggedEntity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=256)),
                ('annotator', models.CharField(max_length=256)),
                ('start_index', models.IntegerField()),
                ('end_index', models.IntegerField()),
                ('tagging_datetime', models.DateTimeField(editable=False)),
                ('doc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entities', to='backend.datafile')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entity_tags', to='backend.tag')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('top_dir', models.CharField(blank=True, max_length=256, null=True, unique=True)),
                ('status', models.CharField(choices=[('ND', 'No Data Imported'), ('DC', 'Directories Created'), ('DA', 'Datasets Imported'), ('C', 'Completed')], default='ND', max_length=4)),
                ('tags', models.ManyToManyField(to='backend.Tag')),
            ],
            options={
                'verbose_name_plural': '     Projects',
            },
        ),
        migrations.CreateModel(
            name='DataSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('data_dir', models.CharField(blank=True, max_length=256, null=True)),
                ('status', models.CharField(choices=[('ND', 'No Data Imported'), ('DA', 'Datasets Imported'), ('WIP', 'Work In Progress'), ('C', 'Completed')], default='ND', max_length=4)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='datasets', to='backend.project')),
            ],
            options={
                'verbose_name_plural': '    Datasets',
            },
        ),
        migrations.AddField(
            model_name='datafile',
            name='dataset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='backend.dataset'),
        ),
    ]
