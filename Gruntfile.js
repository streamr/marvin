/* jshint indent:2,camelcase:false */
/* global module,require */
module.exports = function (grunt) {
  "use strict";

  // Load all grunt tasks defined in package.json
  require('load-grunt-tasks')(grunt);

  // Project configuration.
  grunt.initConfig({


    pkg: grunt.file.readJSON('package.json'),

    jshint: {
      options: {
        'jshintrc': '.jshintrc',
      },
      all: [
        'Gruntfile.js',
      ]
    },

    watch: {
      options: {
        livereload: true
      },
      python: {
        files: [
          'marvin/**/*.py',
          'run_devserver.py',
        ]
      }
    },

    pylint: {
      options: {
        virtualenv: '<%= grunt.option("virtualenv") || "venv" %>',
        rcfile: '.pylintrc',
      },
      marvin: {
        options: {
          ignore: 'tests',
        },
        src: ['marvin', '*.py'],
      },
      marvinTests: {
        options: {
          disable: [
            'missing-docstring',
            'too-many-public-methods',
          ]
        },
        src: ['marvin/tests'],
      }
    },

    // Shortcuts for some often used commands
    shell: {
      options: {
        stderr: true,
      },
      devserver: {
        options: {
          stdout: true,
        },
        command: 'python run_devserver.py'
      },
    },

    clean: {
      python: [
        'marvin/**/*.pyc',
      ],
    },

    concurrent: {
      server: {
        tasks: ['watch', 'shell:devserver'],
        options: {
          logConcurrentOutput: true,
        }
      }
    },

    nose: {
      marvin: {
        options: {
          virtualenv: '<%= grunt.option("virtualenv") || "venv" %>',
          with_coverage: true,
          cover_branches: true,
          cover_package: 'marvin',
          cover_html: true,
          cover_html_dir: 'cover',
        },
        src: 'marvin',
      }
    }

  });


  // Default task
  grunt.registerTask('default', [
    'server',
  ]);
  grunt.registerTask('lint', [
    'jshint',
    'pylint',
  ]);
  grunt.registerTask('test', [
    'nose',
  ]);
  grunt.registerTask('server', [
    'concurrent:server',
  ]);
};
