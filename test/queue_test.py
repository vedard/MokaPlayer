import unittest
from collections import deque

from mokaplayer.core.queue import Queue


class QueueTest(unittest.TestCase):
    def setUp(self):
        self.queue = Queue()
        self.queue.append([1, 2, 3, 4, 5, 6, 7, 8, 9])

    def test_peek(self):
        self.assertEqual(self.queue.peek(), 1)

    def test_next(self):
        self.queue.next()
        self.assertEqual(self.queue.peek(), 2)
        self.assertEqual(self.queue._container,
                         deque([2, 3, 4, 5, 6, 7, 8, 9, 1]))

    def test_next_while_empty(self):
        self.queue.clear()
        self.queue.next()
        self.assertEqual(self.queue.peek(), None)

    def test_prev(self):
        self.queue.prev()
        self.assertEqual(self.queue.peek(), 9)
        self.assertEqual(self.queue._container,
                         deque([9, 1, 2, 3, 4, 5, 6, 7, 8]))

    def test_prev_while_empty(self):
        self.queue.clear()
        self.queue.prev()
        self.assertEqual(self.queue.peek(), None)

    def test_seek(self):
        self.queue.seek(6)
        self.assertEqual(self.queue._container,
                         deque([6, 7, 8, 9, 1, 2, 3, 4, 5]))
        self.assertEqual(self.queue.peek(), 6)

        self.queue.seek(86)
        self.assertEqual(self.queue._container, deque(
            [86, 7, 8, 9, 1, 2, 3, 4, 5, 6]))
        self.assertEqual(self.queue.peek(), 86)

    def test_shuffle(self):
        self.queue.shuffle()
        self.assertEqual(self.queue.peek(), 1)
        self.assertNotEqual(self.queue._container,
                            deque([1, 2, 3, 4, 5, 6, 7, 8, 9]))

    def test_shuffle_when_current_not_in_queue(self):
        self.queue.clear()
        self.queue.append([20, 21, 22, 24])
        self.assertEqual(self.queue.peek(), 1)
        self.assertNotIn(1, self.queue._container)

    def test_append(self):
        self.queue.append(77)
        self.queue.append([1, 2, 5, 89, 45, 23])
        self.assertEqual(self.queue._container,
                         deque([3, 4, 6, 7, 8, 9, 77, 1, 2, 5, 89, 45, 23]))
        self.assertEqual(self.queue.peek(), 1)

        self.queue = Queue()
        self.queue.append([5, 6, 7, 8])
        self.assertEqual(self.queue.peek(), 5)

    def test_prepend(self):
        self.queue.prepend(77)
        self.queue.prepend([23, 8, 9, 3])
        self.assertEqual(self.queue._container,
                         deque([1, 23, 8, 9, 3, 77, 2, 4, 5, 6, 7]))
        self.assertEqual(self.queue.peek(), 1)

        self.queue = Queue()
        self.queue.prepend([5, 6, 7, 8])
        self.assertEqual(self.queue.peek(), 5)

    def test_remove(self):
        self.queue.remove(77)
        self.queue.remove([1, 4, 9])
        self.queue.remove(3)
        self.assertEqual(self.queue._container, deque([2, 5, 6, 7, 8]))
        self.assertEqual(self.queue.peek(), 1)

    def test_clear(self):
        self.queue.clear()
        self.assertEqual(len(self.queue), 0)

    def test_len(self):
        self.assertEqual(len(self.queue), 9)

    def test_pop(self):
        self.queue.pop()
        self.assertIsNone(self.queue.peek())
        self.queue.next()
        self.assertIsNotNone(self.queue.peek())

    def test_iter(self):
        for x in self.queue:
            self.assertIsNotNone(x)
