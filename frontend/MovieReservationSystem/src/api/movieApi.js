import movieClient from "./movieClient";

// GET http://127.0.0.1:8002/api/v1/movies  ->  array of movies
export function getMovies() {
  return movieClient.get("/movies");
}