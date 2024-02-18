from flask import Flask, render_template, request, redirect, url_for, flash
from library import Library
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
lib = Library()
app.secret_key = b'key'
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/list_books', methods=['GET', 'POST'])
def list_books():
    if request.method == 'POST':
        author = request.form.get('author')
        category = request.form.get('category')

        books = lib.list_books()
        filtered_books = []
        categories = set()

        for book in books:
            book_info = book.split(", ")
            book_author = book_info[2].strip()
            book_category = book_info[5].strip()

            author_matches = not author or any(
                author.lower() in author_name.lower() for author_name in book_author.split("/"))
            category_matches = not category or any(
                category.lower() == category_name.lower() for category_name in book_category.split("/"))

            if author_matches and category_matches:
                filtered_books.append({
                    "id": book_info[0].strip(),
                    "title": book_info[1].strip(),
                    "author": book_author,
                    "year": book_info[3].strip(),
                    "pages": book_info[4].strip(),
                    "category": book_category
                })


                categories.update(category_name.title() for category_name in book_category.split("/"))


        categories = sorted(categories)

        return render_template('list_books.html', books=filtered_books, categories=categories)

    else:
        books = lib.list_books()
        formatted_books = []
        categories = set()

        for book in books:
            book_info = book.split(", ")
            book_author = book_info[2].strip()
            book_category = book_info[5].strip()
            formatted_books.append({
                "id": book_info[0].strip(),
                "title": book_info[1].strip(),
                "author": book_author,
                "year": book_info[3].strip(),
                "pages": book_info[4].strip(),
                "category": book_category
            })


            categories.update(book_category.split("/"))


        categories = sorted(categories)

        return render_template('list_books.html', books=formatted_books, categories=categories)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    error = None
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        release_year = request.form['release_year']
        num_pages = request.form['num_pages']
        category = request.form['category']
        result = lib.add_book(title, author, release_year, num_pages, category)
        if result != "Kitap başarıyla eklendi.":
            error = result
        else:
            return redirect(url_for('list_books'))
    return render_template('add_book.html', error=error)


@app.route('/remove_book', methods=['GET', 'POST'])
def remove_book():
    error = None
    if request.method == 'POST':
        id_or_title = request.form['id_or_title']
        books = lib.list_books()
        matching_books = []
        for book in books:
            book_info = book.split(",")
            book_id = book_info[0].strip()
            book_title = book_info[1].strip().lower()
            book_author = book_info[2].strip()

            if id_or_title.lower() == book_title:
                matching_books.append((book_id, book_title,book_author))
        if len(matching_books) > 1:
            return render_template('remove_book_options.html', books=matching_books)
        elif len(matching_books) == 1:
            result = lib.remove_book(matching_books[0][0])
            if result != "Kitap başarıyla silindi.":
                error = result
            else:
                return redirect(url_for('list_books'))
        else:
            result = lib.remove_book(id_or_title)
            if result != "Kitap başarıyla silindi.":
                error = result
            else:
                return redirect(url_for('list_books'))
    return render_template('remove_book.html', error=error)

@app.route('/remove_book_confirm', methods=['POST'])
def remove_book_confirm():
    id_or_title = request.form.get('id_or_title')
    if id_or_title:
        result = lib.remove_book(id_or_title)
        flash(result)
        return redirect(url_for('list_books'))
    else:
        flash("Kitap ID'si veya Adı alınamadı.")
        return redirect(url_for('remove_book_options'))


from bs4 import BeautifulSoup
import requests

@app.route('/book_detail/<book_name>')
def book_detail(book_name):
    book_details = get_book_details(book_name)
    if book_details:
        return render_template('book_detail.html', book_details=book_details)
    else:
        return render_template('detail_not_found.html')

def get_book_details(book_name):
    url = f"https://www.goodreads.com/search?q={book_name}&search_type=books"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        first_book_link = soup.find("a", class_="bookTitle", href=True)

        if first_book_link:
            book_url = "https://www.goodreads.com" + first_book_link['href']
            book_response = requests.get(book_url)

            if book_response.status_code == 200:
                book_soup = BeautifulSoup(book_response.text, 'html.parser')
                image = book_soup.find("img", class_="ResponsiveImage")
                book_image = image['src'] if image else "No image available"
                summary = book_soup.find("span", class_="Formatted")
                book_summary = summary.text.strip() if summary else "No summary available"

                return {
                    "image": book_image,
                    "summary": book_summary
                }

    return None


if __name__ == '__main__':
    app.run(debug=True)
