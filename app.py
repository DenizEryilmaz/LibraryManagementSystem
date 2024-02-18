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

@app.route('/list_books')
def list_books():
    books = lib.list_books()
    formatted_books = []
    for book in books:
        book_info = book.split(", ")
        book_id = book_info[0].strip()
        book_title = book_info[1].strip()
        book_author = book_info[2].strip()
        book_year = book_info[3].strip()
        book_pages = book_info[4].strip()
        formatted_books.append({
            "id": book_id,
            "title": book_title,
            "author": book_author,
            "year": book_year,
            "pages": book_pages
        })
    return render_template('list_books.html', books=formatted_books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    error = None
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        release_year = request.form['release_year']
        num_pages = request.form['num_pages']
        result = lib.add_book(title, author, release_year, num_pages)
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
