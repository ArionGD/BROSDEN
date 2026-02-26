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
                    orange: '#E75A27',
                },
            },
        },
    },
    plugins: [],
}
