import pytest
import datetime
from fastapi import HTTPException
from app.services.movie_service import create_movie, update_movie, get_movie_by_id, list_movies, delete_movie
from app.schemas.movie import MovieCreate, Movie

def test_list_movie_empty_list(mocker):
    mocker.patch("app.repositories.movie_repo.load_all", return_value=[])
    movies = list_movies()
    assert movies == []

def test_list_movie_has_movies(mocker):
    mocker.patch("app.repositories.movie_repo.load_all", return_value=[
    {
        "id": "1234",
        "title": "Test",
        "genre": "Horror",
        "release": "2022-01-01",
        "description": "Testing Description",
        "duration": 90
    }])
    movies = list_movies()
    assert movies[0].id == "1234"
    assert movies[0].title == "Test"
    assert movies[0].genre == "Horror"
    assert movies[0].release == datetime.date(2022, 1, 1)
    assert movies[0].description == "Testing Description"
    assert movies[0].duration == 90
    assert len(movies) == 1

def test_create_movie_adds_movie(mocker):
    mocker.patch("app.repositories.movie_repo.load_all", return_value=[])
    mock_save = mocker.patch("app.repositories.movie_repo.save_all")
    mocker.patch("uuid.uuid4", return_value="1234")

    payload = MovieCreate(
        title="Test", genre="Horror", release="2022-01-01", description="Testing Description", duration=90
    )

    movie = create_movie(payload)

    assert movie.id == "1234"
    assert movie.title == "Test"
    assert movie.genre == "Horror"
    assert movie.release == datetime.date(2022, 1, 1)
    assert movie.description == "Testing Description"
    assert movie.duration == 90
    assert mock_save.called

def test_create_movie_collides_id(mocker):
    mocker.patch("app.repositories.movie_repo.load_all", return_value=[
    {
        "id": "1234",
        "title": "Test",
        "genre": "Horror",
        "release": "2022-01-01",
        "description": "Testing Description",
        "duration": 90
    }])
    mock_save = mocker.patch("app.repositories.movie_repo.save_all")
    mocker.patch("uuid.uuid4", return_value="1234")
    payload = MovieCreate(
        title="AnotherMovie", genre="Psychological Thriller", release="2020-01-01", description="A Colliding Movie", duration=20
    )
    with pytest.raises(HTTPException) as ex:
        create_movie(payload)
    assert ex.value.status_code == 409
    assert ex.value.detail == "ID collision; retry"

def test_create_movie_strips_whitespace(mocker):
    mocker.patch("app.repositories.movie_repo.load_all", return_value=[])
    mock_save = mocker.patch("app.repositories.movie_repo.save_all")
    mocker.patch("uuid.uuid4", return_value="1234")
    payload = MovieCreate(
        title="    Lots of White Space!     ", genre="Horror    ", release="2022-01-01", description="  Testing Description     ", duration=90
    )
    movie = create_movie(payload)
    assert movie.title == "Lots of White Space!"
    assert movie.genre == "Horror"
    assert movie.description == "Testing Description"
    assert mock_save.called

def test_get_movie_by_id_valid_id(mocker):
    mocker.patch("app.repositories.movie_repo.load_all", return_value=[
    {
        "id": "1234",
        "title": "Test",
        "genre": "Horror",
        "release": "2022-01-01",
        "description": "Testing Description",
        "duration": 90
    }])
    movie = get_movie_by_id("1234")
    assert movie.id == "1234"
    assert movie.title == "Test"
    assert isinstance(movie, Movie)

def test_get_movie_by_id_invalid_id(mocker):
    mocker.patch("app.repositories.movie_repo.load_all", return_value=[])
    with pytest.raises(HTTPException) as ex:
        get_movie_by_id("1234")
    assert ex.value.status_code == 404
    assert "not found" in ex.value.detail

def test_update_movie_valid_update(mocker):
    mocker.patch("app.repositories.movie_repo.load_all", return_value=[
    {
        "id": "1234",
        "title": "Test",
        "genre": "Horror",
        "release": "2022-01-01",
        "description": "Testing Description",
        "duration": 90
    }])
    mock_save = mocker.patch("app.repositories.movie_repo.save_all")
    payload = MovieCreate(
        title="Updated Test", genre="Horror/Psychological Thriller", release="2022-01-01", description="Now I have updated this movie!", duration=90
    )
    movie = update_movie("1234", payload)
    assert movie.title == "Updated Test"
    assert movie.genre == "Horror/Psychological Thriller"
    assert movie.description == "Now I have updated this movie!"
    assert mock_save.called

def test_update_movie_invalid_id(mocker):
    mocker.patch("app.repositories.movie_repo.load_all", return_value=[])
    mock_save = mocker.patch("app.repositories.movie_repo.save_all")
    payload = MovieCreate(
        title="Invalid Test", genre="Thriller", release="2022-01-01", description="This update should NOT work", duration=90
    )
    with pytest.raises(HTTPException) as ex:
        update_movie("1234", payload)
    assert ex.value.status_code == 404
    assert "not found" in ex.value.detail

def test_delete_movie_valid_movie(mocker):
    mocker.patch("app.repositories.movie_repo.load_all", return_value=[
    {
        "id": "1234",
        "title": "Test",
        "genre": "Horror",
        "release": "2022-01-01",
        "description": "Testing Description",
        "duration": 90
    }])
    mock_save = mocker.patch("app.repositories.movie_repo.save_all")
    delete_movie("1234")
    saved_movies = mock_save.call_args[0][0]
    assert all(m['id'] != "1234" for m in saved_movies)
    assert mock_save.called

def test_delete_movie_invalid_movie(mocker):
    mocker.patch("app.repositories.movie_repo.load_all", return_value=[])
    mock_save = mocker.patch("app.repositories.movie_repo.save_all")
    with pytest.raises(HTTPException) as ex:
        delete_movie("1234")
    assert ex.value.status_code == 404
    assert "not found" in ex.value.detail
