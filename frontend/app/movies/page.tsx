import { useState, useEffect } from 'react';

'use client';


interface Movie {
    id: string;
    title: string;
    year: number;
    genre: string[];
    rating: number;
    poster: string;
    description: string;
}

export default function MoviesPage() {
    const [movies, setMovies] = useState<Movie[]>([]);
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchMovies();
    }, []);

    const fetchMovies = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/movies');
            if (!response.ok) throw new Error('Failed to fetch movies');
            const data = await response.json();
            setMovies(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    const filtered = movies.filter(movie =>
        movie.title.toLowerCase().includes(search.toLowerCase())
    );

    if (loading) return <div className="p-8">Loading...</div>;
    if (error) return <div className="p-8 text-red-500">Error: {error}</div>;

    return (
        <div className="p-8">
            <h1 className="text-4xl font-bold mb-8">Movies</h1>
            
            <input
                type="text"
                placeholder="Search movies..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full p-2 border rounded mb-8"
            />

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {filtered.map(movie => (
                    <div key={movie.id} className="border rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition">
                        <img src={movie.poster} alt={movie.title} className="w-full h-64 object-cover" />
                        <div className="p-4">
                            <h2 className="font-bold text-lg">{movie.title}</h2>
                            <p className="text-sm text-gray-600">{movie.year}</p>
                            <p className="text-yellow-500 font-semibold">★ {movie.rating}</p>
                            <p className="text-sm mt-2">{movie.description}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}