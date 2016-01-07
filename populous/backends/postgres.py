from itertools import islice

from populous.exceptions import BackendError
from .base import Backend

try:
    import psycopg2
except ImportError:
    raise BackendError("You must install 'psycopg2' in order to use the "
                       "Postgresql backend")


BATCH_SIZE = 10000


def batches(generator, length):
    for _ in xrange(length // BATCH_SIZE):
        yield BATCH_SIZE, islice(generator, BATCH_SIZE)

    if length % BATCH_SIZE:
        yield length % BATCH_SIZE, islice(generator, BATCH_SIZE)


class Postgres(Backend):
    def __init__(self, *args, **kwargs):
        super(Postgres, self).__init__(*args, **kwargs)

        try:
            self.conn = psycopg2.connect(**kwargs)
        except psycopg2.DatabaseError as e:
            raise BackendError("Error connecting to Postgresql DB: {}"
                               .format(e))

    def transaction(self):
        with self.conn:
            return self.conn.cursor()

    def generate(self, item, cursor):
        for size, batch in batches(item.generate(), item.total):
            stmt = "INSERT INTO {} ({}) VALUES {}".format(
                item.table,
                ", ".join(field.name for field in item.fields),
                ", ".join("({})".format(
                    ", ".join("%s" for _ in xrange(len(item.fields)))
                ) for _ in xrange(size))
            )

            try:
                cursor.execute(stmt, tuple(v for vs in batch for v in vs))
            except psycopg2.DatabaseError as e:
                raise BackendError("Error during the generation of "
                                   "'{}': {}".format(item.name, e.message))

            yield size

    def close(self):
        if not self.closed:
            try:
                self.conn.close()
            finally:
                self.closed = True
