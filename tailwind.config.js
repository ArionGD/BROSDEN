/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./**/templates/**/*.html",
        "./**/static/**/*.js",
    ],
    theme: {
        extend: {
            colors: {
                arion: {
                    blue: '#1A73E8',
                    'blue-light': '#4285F4', // More vibrant, lighter blue
                    orange: '#E75A27',
                },
            },
        },
    },
    plugins: [],
}
