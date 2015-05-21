// Include gulp
var gulp = require('gulp');

gulp.task('fonts', function() {
    return gulp.src('pypics/static/components/font-awesome/fonts/*')
        .pipe(gulp.dest('pypics/static/sdist/fonts/'));
});


// Default Task
gulp.task('default', ['fonts']);
