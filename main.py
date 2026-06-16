from dataclasses import dataclass, field


@dataclass
class Book:
    book_id: int
    title: str
    author: str
    total_copies: int
    available_copies: int

    def borrowed_count(self):
        return self.total_copies - self.available_copies


@dataclass
class Reader:
    reader_id: int
    name: str
    borrowed_books: list[int] = field(default_factory=list)


class Library:
    def __init__(self):
        self.books = [
            Book(1, "Lalka", "Bolesław Prus", 5, 2),
            Book(2, "Dziady", "Adam Mickiewicz", 3, 0),
            Book(3, "Ferdydurke", "Witold Gombrowicz", 4, 1),
            Book(4, "Zbrodnia i kara", "Fiodor Dostojewski", 2, 0),
            Book(5, "Pan Tadeusz", "Adam Mickiewicz", 6, 4),
        ]

        self.readers = [
            Reader(1, "Jan Kowalski", [1, 2]),
            Reader(2, "Anna Nowak", [1]),
            Reader(3, "Piotr Zieliński", []),
        ]

        # book_id -> lista reader_id
        self.reservations = {}

        # lista próśb o przedłużenie: (reader_id, book_id)
        self.extension_requests = [
            (1, 2),
            (2, 1),
        ]

    
    # Przyjmuje inne funkcje jako argumenty:
    def display_collection(
        self,
        collection,
        predicate=lambda item: True,
        formatter=lambda item: str(item),
        sort_key=lambda item: str(item)
    ):
        result = sorted(
            filter(predicate, collection),
            key=sort_key
        )

        return "\n".join(map(formatter, result)) or "Brak wyników."

       # Funkcja zwracająca inną funkcję
    def make_phrase_filter(self, phrase):
        phrase = phrase.lower().strip()

        return lambda book: (
            phrase in book.title.lower()
            or phrase in book.author.lower()
        )

    # Funkcje pomocnicze
    def get_book_by_id(self, book_id):
        return next(
            filter(lambda book: book.book_id == book_id, self.books),
            None
        )

    def get_reader_by_id(self, reader_id):
        return next(
            filter(lambda reader: reader.reader_id == reader_id, self.readers),
            None
        )

    def format_book(self, book):
        return (
            f"[{book.book_id}] {book.title} — {book.author} | "
            f"dostępne: {book.available_copies}/{book.total_copies}"
        )

    def format_reader(self, reader):
        return f"[{reader.reader_id}] {reader.name}"

    # Wyszukiwanie i filtrowanie katalogu
    def filter_catalog(self, phrase="", only_available=False):
        phrase_filter = self.make_phrase_filter(phrase)

        return list(filter(
            lambda book: phrase_filter(book)
            and (not only_available or book.available_copies > 0),
            self.books
        ))

    # Sortowanie katalogu
    def sort_catalog(self, books=None, sort_by="title"):
        books = books if books is not None else self.books

        sort_options = {
            "title": lambda book: book.title.lower(),
            "author": lambda book: book.author.lower(),
            "available": lambda book: book.available_copies
        }

        return sorted(
            books,
            key=sort_options.get(sort_by, sort_options["title"])
        )

    def show_catalog(self, phrase="", only_available=False, sort_by="title"):
        filtered_books = self.filter_catalog(phrase, only_available)
        sorted_books = self.sort_catalog(filtered_books, sort_by)

        return "\n".join(map(self.format_book, sorted_books)) or "Brak książek."

    # Wypożyczanie książki
    def borrow_book(self, reader_id, book_id):
        reader = self.get_reader_by_id(reader_id)
        book = self.get_book_by_id(book_id)

        if reader is None:
            return "Nie znaleziono czytelnika."

        if book is None:
            return "Nie znaleziono książki."

        if book.available_copies <= 0:
            return "Książka jest niedostępna. Możesz ją zarezerwować."

        book.available_copies -= 1
        reader.borrowed_books = reader.borrowed_books + [book_id]

        return f"Wypożyczono książkę: {book.title}"

    # Zwrot książki
    def return_book(self, reader_id, book_id):
        reader = self.get_reader_by_id(reader_id)
        book = self.get_book_by_id(book_id)

        if reader is None:
            return "Nie znaleziono czytelnika."

        if book is None:
            return "Nie znaleziono książki."

        if book_id not in reader.borrowed_books:
            return "Ten czytelnik nie ma wypożyczonej tej książki."

        reader.borrowed_books = [
            borrowed_id
            for borrowed_id in reader.borrowed_books
            if borrowed_id != book_id
        ]

        book.available_copies += 1

        return f"Zwrócono książkę: {book.title}"

    # Rezerwacja niedostępnego tytułu
    def reserve_book(self, reader_id, book_id):
        reader = self.get_reader_by_id(reader_id)
        book = self.get_book_by_id(book_id)

        if reader is None:
            return "Nie znaleziono czytelnika."

        if book is None:
            return "Nie znaleziono książki."

        if book.available_copies > 0:
            return "Książka jest dostępna, więc nie trzeba jej rezerwować."

        current_reservations = self.reservations.get(book_id, [])

        if reader_id in current_reservations:
            return "Masz już rezerwację tej książki."

        self.reservations[book_id] = current_reservations + [reader_id]

        return f"Zarezerwowano książkę: {book.title}"

    def has_reservation(self, book_id):
        return len(self.reservations.get(book_id, [])) > 0

    # Prośba o przedłużenie
    def request_extension(self, reader_id, book_id):
        reader = self.get_reader_by_id(reader_id)
        book = self.get_book_by_id(book_id)

        if reader is None:
            return "Nie znaleziono czytelnika."

        if book is None:
            return "Nie znaleziono książki."

        if book_id not in reader.borrowed_books:
            return "Nie możesz przedłużyć książki, której nie masz wypożyczonej."

        request = (reader_id, book_id)

        if request in self.extension_requests:
            return "Prośba o przedłużenie już istnieje."

        self.extension_requests = self.extension_requests + [request]

        return f"Wysłano prośbę o przedłużenie książki: {book.title}"

    # Info o rezerwacji przy obsłudze przedłużenia
    def show_extension_requests(self):
        def format_request(request):
            reader_id, book_id = request

            reader = self.get_reader_by_id(reader_id)
            book = self.get_book_by_id(book_id)

            reservation_info = (
                "TAK — istnieje rezerwacja"
                if self.has_reservation(book_id)
                else "NIE — brak rezerwacji"
            )

            return (
                f"Czytelnik: {reader.name if reader else 'Nieznany'} | "
                f"Książka: {book.title if book else 'Nieznana'} | "
                f"Rezerwacja: {reservation_info}"
            )

        return "\n".join(map(format_request, self.extension_requests)) or "Brak próśb o przedłużenie."

    # Statystyki bibliotekarza
    def librarian_statistics(self):
        popular_book = max(
            self.books,
            key=lambda book: book.total_copies - book.available_copies,
            default=None
        )

        active_loans_count = sum(
            map(lambda reader: len(reader.borrowed_books), self.readers)
        )

        readers_with_counts = [
            {
                "reader": reader.name,
                "borrowed_count": len(reader.borrowed_books)
            }
            for reader in self.readers
        ]

        sorted_readers = sorted(
            readers_with_counts,
            key=lambda item: item["borrowed_count"],
            reverse=True
        )

        reservations_summary = {
            book.title: len(self.reservations.get(book.book_id, []))
            for book in self.books
            if len(self.reservations.get(book.book_id, [])) > 0
        }

        readers_text = "\n".join(map(
            lambda item: f"{item['reader']} — {item['borrowed_count']} wypożyczonych książek",
            sorted_readers
        ))

        reservations_text = "\n".join(map(
            lambda item: f"{item[0]} — liczba rezerwacji: {item[1]}",
            reservations_summary.items()
        )) or "Brak rezerwacji."

        popular_book_text = (
            f"{popular_book.title} — wypożyczone sztuki: {popular_book.borrowed_count()}"
            if popular_book
            else "Brak książek."
        )

        return (
            "STATYSTYKI BIBLIOTEKARZA\n"
            "-----------------------\n"
            f"Najpopularniejsza książka: {popular_book_text}\n"
            f"Liczba aktywnych wypożyczeń ogółem: {active_loans_count}\n\n"
            "Czytelnicy wg liczby wypożyczeń:\n"
            f"{readers_text or 'Brak czytelników.'}\n\n"
            "Rezerwacje:\n"
            f"{reservations_text}"
        )

    def show_readers(self):
        return "\n".join(map(self.format_reader, self.readers)) or "Brak czytelników."


def read_int(message):
    try:
        return int(input(message))
    except ValueError:
        return None


def choose_reader(library):
    print("\nDostępni czytelnicy:")
    print(library.show_readers())

    reader_id = read_int("Podaj ID czytelnika: ")

    if library.get_reader_by_id(reader_id) is None:
        print("Nie znaleziono czytelnika.")
        return None

    return reader_id


def reader_menu(library):
    reader_id = choose_reader(library)

    if reader_id is None:
        return

    while True:
        print("\n--- MENU CZYTELNIKA ---")
        print("1. Pokaż katalog")
        print("2. Wyszukaj książkę")
        print("3. Pokaż tylko dostępne książki")
        print("4. Posortuj katalog")
        print("5. Wypożycz książkę")
        print("6. Zwróć książkę")
        print("7. Zarezerwuj niedostępną książkę")
        print("8. Poproś o przedłużenie")
        print("0. Powrót")

        choice = input("Wybierz opcję: ")

        if choice == "1":
            print("\nKATALOG:")
            print(library.show_catalog())

        elif choice == "2":
            phrase = input("Podaj frazę z tytułu lub autora: ")
            print(library.show_catalog(phrase=phrase))

        elif choice == "3":
            print(library.show_catalog(only_available=True))

        elif choice == "4":
            print("Sortuj po: title / author / available")
            sort_by = input("Wybór: ")
            print(library.show_catalog(sort_by=sort_by))

        elif choice == "5":
            book_id = read_int("Podaj ID książki: ")
            print(library.borrow_book(reader_id, book_id))

        elif choice == "6":
            book_id = read_int("Podaj ID książki: ")
            print(library.return_book(reader_id, book_id))

        elif choice == "7":
            book_id = read_int("Podaj ID książki: ")
            print(library.reserve_book(reader_id, book_id))

        elif choice == "8":
            book_id = read_int("Podaj ID książki: ")
            print(library.request_extension(reader_id, book_id))

        elif choice == "0":
            break

        else:
            print("Nieprawidłowa opcja.")


def librarian_menu(library):
    while True:
        print("\n--- MENU BIBLIOTEKARZA ---")
        print("1. Pokaż katalog")
        print("2. Wyszukaj książkę")
        print("3. Pokaż tylko dostępne książki")
        print("4. Posortuj katalog")
        print("5. Obsłuż prośby o przedłużenie")
        print("6. Statystyki")
        print("0. Powrót")

        choice = input("Wybierz opcję: ")

        if choice == "1":
            print("\nKATALOG:")
            print(library.show_catalog())

        elif choice == "2":
            phrase = input("Podaj frazę z tytułu lub autora: ")
            print(library.show_catalog(phrase=phrase))

        elif choice == "3":
            print(library.show_catalog(only_available=True))

        elif choice == "4":
            print("Sortuj po: title / author / available")
            sort_by = input("Wybór: ")
            print(library.show_catalog(sort_by=sort_by))

        elif choice == "5":
            print("\nPROŚBY O PRZEDŁUŻENIE:")
            print(library.show_extension_requests())

        elif choice == "6":
            print()
            print(library.librarian_statistics())

        elif choice == "0":
            break

        else:
            print("Nieprawidłowa opcja.")


def main():
    library = Library()

    while True:
        print("\n=== SYSTEM BIBLIOTECZNY ===")
        print("1. Czytelnik")
        print("2. Bibliotekarz")
        print("0. Wyjście")

        choice = input("Wybierz rolę: ")

        if choice == "1":
            reader_menu(library)

        elif choice == "2":
            librarian_menu(library)

        elif choice == "0":
            print("Zakończono program.")
            break

        else:
            print("Nieprawidłowa opcja.")


if __name__ == "__main__":
    main()