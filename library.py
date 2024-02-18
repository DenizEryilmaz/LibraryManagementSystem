class Library:
    def __init__(self):
        self.books_file = "books.txt"
        self.file = open(self.books_file, "a+", encoding="utf-8")

    def __del__(self):
        self.file.close()

    def list_books(self):
        self.file.seek(0)
        return self.file.read().splitlines()

    def add_book(self, title, author, release_year, num_pages, category):
        if not all([title, author, release_year, num_pages, category]):
            return "Eksik bilgi. Lütfen tüm alanları doldurun."
        try:
            int(release_year)
            int(num_pages)
        except ValueError:
            return "Yıl ve sayfa sayısı için geçerli bir sayı giriniz."

        title_lower = title.strip().lower()
        author_lower = author.strip().lower()
        books = [book.split(",") for book in self.list_books()]

        existing_books = {(book_info[1].strip().lower(), book_info[2].strip().lower()) for book_info in books}

        if (title_lower, author_lower) in existing_books:
            return "Bu kitap zaten mevcut."

        max_id = max(int(book_info[0]) for book_info in books) if books else 0
        new_id = max_id + 1

        self.file.write(f"{new_id}, {title}, {author}, {release_year}, {num_pages}, {category}\n")
        return "Kitap başarıyla eklendi."

    def remove_book(self, input_value):
        input_value_lower = input_value.lower()
        books = self.list_books()
        if not books:
            return "Kitap bulunamadı."

        found_books = set()
        for book in books:
            book_info = book.split(",")
            book_id = book_info[0].strip()
            book_title = book_info[1].strip().lower()
            book_author = book_info[2].strip().lower()
            if book_id == input_value_lower or book_title == input_value_lower:
                found_books.add((book_id, book_title, book_author))

        if not found_books:
            return "Kitap bulunamadı."

        if len(found_books) == 1:
            book_id = found_books.pop()[0]
            self._delete_book_by_id(book_id)
            return "Kitap başarıyla silindi."

        print("Aynı isimde birden fazla kitap bulundu:")
        for book_id, book_title, book_author in found_books:
            print(f"ID: {book_id}, Kitap Adı: {book_title}, Yazarı: {book_author}")

        while True:
            selected_id = input("Silmek için kitabın ID değerini giriniz, ana menüye dönmek için 'x' değerini giriniz ")
            if selected_id.lower() == "x":
                return "x"
            elif selected_id.isdigit():
                selected_id = selected_id.strip()
                if any(book[0] == selected_id for book in found_books):
                    self._delete_book_by_id(selected_id)
                    return "Kitap silindi."
                else:
                    print("Hatalı ID. Lütfen tekrar giriniz.")
            else:
                print("Hatalı girdi.")

    def _delete_book_by_id(self, id):
        with open(self.books_file, "r", encoding="utf-8") as file:
            books = file.readlines()
        remaining_books = [book for book in books if book.split(",")[0].strip() != id]
        with open(self.books_file, "w", encoding="utf-8") as file:
            file.writelines(remaining_books)

    def print_books(self):
        books = self.list_books()
        if not books:
            print("Kitap bulunamadı.")
            return "x"

        book_info_dict = {}
        for book in books:
            book_info = book.split(",")
            book_id = book_info[0].strip()
            book_title = book_info[1].strip()
            book_author = book_info[2].strip()
            book_release_year = book_info[3].strip()
            book_num_pages = book_info[4].strip()
            book_category = book_info[5].strip()
            book_info_dict[book_id] = (book_title, book_author, book_release_year, book_num_pages, book_category)
            print(f"ID: {book_id}, Kitap Adı: {book_title}, Yazarı: {book_author}, Kategori: {book_category}")

        user_input = input(
            "Kitap hakkında daha fazla bilgi almak için ID'sini giriniz, ana menüye dönmek için 'x'i tuşlayınız: ")
        if user_input.lower() == "x":
            return "x"
        elif user_input.isdigit():
            book_info = book_info_dict.get(user_input)
            if book_info:
                print(f"Kitap Adı: {book_info[0]}")
                print(f"Yazarı: {book_info[1]}")
                print(f"Yılı: {book_info[2]}")
                print(f"Sayfa sayısı: {book_info[3]}")
                print(f"Kategori: {book_info[4]}")
                while True:
                    action = input("Seçili kitabı silmek için 'r' , Ana menüye dönmek için 'x' yazınız: ")
                    if action.lower() == "r":
                        self.remove_book(user_input)
                        print("Kitap silindi.")
                        return "x"
                    elif action.lower() == "x":
                        return "x"
                    else:
                        print("Hatalı Girdi.")
            else:
                print("Belirtilen ID'ye ait kitap bulunamadı")
        else:
            print("Hatalı Girdi.")

    def select_action(self):
        while True:
            print(" Menü ")
            print("1) Kitapları Listele")
            print("2) Kitap Ekle")
            print("3) Kitap Sil")

            choice = input("Bir menü seçiniz. (1-3): ")

            if choice == "1":
                self.print_books()

            elif choice == "2":
                title = input("Kitap adı: ")
                author = input("Yazarı: ")
                release_year = input("Yılı: ")
                num_pages = input("Sayfa Sayısı: ")
                category = input("Kategori: ")
                result = self.add_book(title, author, release_year, num_pages, category)
                print(result)

            elif choice == "3":
                id = input("Silmek istediğiniz kitabın Adı Ya da ID'sini giriniz: ")
                result = self.remove_book(id)
                print(result)

            else:
                print("Hatalı giriş yaptınız.")


if __name__ == "__main__":
    lib = Library()
    lib.select_action()
