# Generated by Django 4.2.6 on 2023-11-13 19:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("created_at", models.DateField()),
                ("updated_at", models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("price", models.DecimalField(decimal_places=4, max_digits=100)),
                ("quantity", models.DecimalField(decimal_places=4, max_digits=100)),
                ("script", models.CharField(max_length=10)),
                ("created_at", models.DateField(auto_now=True)),
                (
                    "buyer_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="buyer_transactions",
                        to="MatchingEngine.user",
                    ),
                ),
                (
                    "seller_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="seller_transactions",
                        to="MatchingEngine.user",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="OrderBook",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("script", models.CharField(max_length=10)),
                ("side", models.CharField(max_length=5)),
                ("price", models.DecimalField(decimal_places=4, max_digits=100)),
                ("quantity", models.DecimalField(decimal_places=4, max_digits=100)),
                (
                    "filled_quantity",
                    models.DecimalField(decimal_places=4, max_digits=100),
                ),
                (
                    "remaining_quantity",
                    models.DecimalField(decimal_places=4, max_digits=100),
                ),
                ("status", models.CharField(default="Pending", max_length=10)),
                ("created_at", models.DateField()),
                ("updated_at", models.DateField()),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="MatchingEngine.user",
                    ),
                ),
            ],
        ),
    ]