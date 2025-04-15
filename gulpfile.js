const gulp = require('gulp');
const htmlmin = require('gulp-htmlmin');
const cleanCSS = require('gulp-clean-css');
const uglify = require('gulp-uglify');

function minifyHtml() {
    return gulp.src('templates/**/*.html')
        .pipe(htmlmin({
            collapseWhitespace: true,
            removeComments: true,
            ignoreCustomFragments: [/\{\%[\s\S]*?\%\}/, /\{\{[\s\S]*?\}\}/] // ignora Jinja2
        }))
        .pipe(gulp.dest('prod/templates'));
}

exports.default = minifyHtml;

function minifyCSS() {
    return gulp.src('static/css/**/*.css')
        .pipe(cleanCSS())
        .pipe(gulp.dest('prod/static/css'));
}

exports.default = minifyCSS;

function minifyJS() {
    return gulp.src('static/js/**/*.js')
        .pipe(uglify())
        .pipe(gulp.dest('prod/static/js'));
}

exports.default = minifyJS;