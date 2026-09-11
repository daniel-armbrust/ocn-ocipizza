from pizzas.create_tables import create_tables
from pizzas.load_pizzas import load_pizzas
from pizzas.upload_images import upload_images

def main():
    print("Starting seed")

    create_tables()
    load_pizzas()
    upload_images()

    print("Seed completed")


if __name__ == "__main__":
    main()