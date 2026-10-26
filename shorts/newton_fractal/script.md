# Guión

¿Puede una ecuación generar un fractal?

Empezemos en el plano complejo, aquí, cualquier número, z, es igual a una parte real y una imaginaria.

Ahora, tomemos una ecuación, digamos, z^3 = 1

Esta ecuación tiene 3 soluciones o raíces. Esas tres soluciones están dentro en un círculo de radio 1. La primera solución es el número 1, tal cual, y la pintamos de azul.

La segunda solución es el número -1/2 + raíz de 3 sobre 2i y la pintamos de amarillo.

La tercera solución es el número -1/2 - raíz de 3 sobre 2 i y la pintamos de rojo

Ahora bien, ¿cómo se obtienen estas soluciones? pues de muchas formas, pero hoy hablaremos de una manera muy popular de encontrar raíces de ecuaciones en física, matemáticas e ingeniería: El método de Newton-Rapshon.

Este método es probablemente el más famoso de los llamados métodos iterativos, en donde uno propone una solución inicial y luego la va mejorando. Esta es la fórmula general del método.

En nuestro caso, toma esta forma.

Ahora, proponemos un número complejo,  zeta 0, que será nuestra propuesta inicial de solución, y aplicamos la fórmula para obtener el zeta 1.

Así, hacemos lo mismo para obtener el zeta 2, luego el zeta 3 y así sucesivamente hasta ver a qué valor converge el método de Newton-Raphson, en este caso, el 1.

Gráficamente, todo el proceso que hemos hecho antes, se ve así, proponemos un zeta 0 y nos movemos con cada iteración, aquí las flechas indicand ese movimiento hasta llegar a la solución, que en este caso era el número 1.

Como se ve, en este caso el zeta 0 estaba más cerca de la segunda solución, pero terminó aproximando a la primera.

Ahora hagamos lo mismo para obtener la segunda solución, proponemos un z0, usamos el método de Newton-Rapshon, que gráficamente se ve así, y dejamos marcado el zeta 0 original. De manera análoga al caso anterior, el zeta 0 de la segunda solución estaba más cerca de una solución distinta a la que terminó por aproximar.

Finalmente, obtenemos la tercera solución, proponemos un zeta 0, usamos Newton-Rapshon hasta que obtenemos la tecerca solución y dejamos marcado el original. Otra vez, el zeta 0 de la tercerca solución comenzó mucho más cerca de otra solución, la segunda en este caso, pero terminó por aproximar la tercera. 

Ahora bien, si de repente usáramos muchos puntos en el plano complejo como zeta 0s y aplicáramos el método de Newton-Rapshon a toodos ellos, veríamos cómo cada uno se pinta del color de la solución que aproxima.

Y si usáramos muchísimos más puntos, veríamos cómo el proceso de Newton-Rapshon genera formas cada vez más sorprendetes hasta formar un fractal conocido como **el fractal de Newton** de la ecuación en cuestion. Si hacemos zoom infintamente, vemos cómo la misma figura aparece una y otra vez. 

Como quizá pudieron ver, obtivimos este fractal al  resolver la ecuación del principio del vídeo usando el método de Newton-Rapshon, lo que indica que fractales distintos pueden obtenerse si usamos el mismo método para resolver diferentes ecuaciones.

Si te ha gustado, sígueme para más matemáticas visuales.