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
          'manage.py',
        ]
      },
      docs: {
        files: [
          'docs/*.rst'
        ],
        tasks: ['shell:sphinx']
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
            'invalid-name',
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
        command: 'python manage.py runserver'
      },
      sphinx: {
        options: {
          stdout: true,
          stderr: true,
          failOnError: true,
        },
        command: 'sphinx-build -a -E -W -b html docs ghdist'
      },
      archive_static: {
        options: {
          stdout: true,
        },
        command: [
          'cd marvin/static',
          'tar czf ../../ghdist/static.tar.gz *',
        ].join(' && '),
      },
    },

    clean: {
      python: [
        'marvin/**/*.pyc',
        'marvin.egg-info',
      ],
      dist: [
        'dist',
        'ghdist',
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
          stop: grunt.option('dontstop') ? false : true,
          with_coverage: true,
          cover_branches: true,
          cover_package: 'marvin',
          cover_html: true,
          cover_html_dir: 'ghdist/coverage',
        },
        src: 'marvin',
      }
    },
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
  grunt.registerTask('build', [
    'shell:sphinx',
    'shell:archive_static',
  ]);
};
