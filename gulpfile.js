var gulp = require("gulp");
var sass = require("gulp-sass");
var less = require("gulp-less");
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var minify = require('gulp-minify-css');
var imagemin = require("gulp-imagemin");
var cache = require("gulp-cache");

gulp.task("sass", function() {
  return gulp.src("static/classy/scss/**/*.scss")
    .pipe(sass())
    .pipe(gulp.dest("static/classy/css"))
});

gulp.task("less", function() {
  return gulp.src("static/classy/less/style.less")
    .pipe(less())
    .pipe(gulp.dest("static/classy/css"))
});

// javascript optimization
gulp.task('js', function(){
  gulp.src('static/classy/js/*.js')
   .pipe(concat('script.js'))
   .pipe(uglify())
   .pipe(gulp.dest('static/classy/js/dist'));
});

// css optimization
gulp.task('css', function(){
  gulp.src('static/classy/css/*.css')
   .pipe(concat('styles.css'))
   .pipe(minify())
   .pipe(gulp.dest('static/classy/css/dist'));
});

// images optimization
gulp.task("images", function() {
  return gulp.src("static/classy/images/**/*.+(png|jpg|gif|svg)")
    .pipe(cache(imagemin({
      interlaced: true
    })))
    .pipe(gulp.dest("static/classy/images/dist"))
});

gulp.task("watch", ["sass", "less"], function() {
  gulp.watch("static/classy/scss/**/*.scss" , ["sass"]);
  gulp.watch("static/classy/less/**/*.less" , ["less"]);
});
