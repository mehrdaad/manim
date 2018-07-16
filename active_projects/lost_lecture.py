from __future__ import absolute_import
from big_ol_pile_of_manim_imports import *

COBALT = "#0047AB"

class Orbiting(ContinualAnimation):
    CONFIG = {
        "rate": 0.3,
    }

    def __init__(self, planet, star, ellipse, **kwargs):
        self.planet = planet
        self.star = star
        self.ellipse = ellipse
        # Proportion of the way around the ellipse
        self.proportion = 0
        planet.move_to(ellipse.point_from_proportion(0))

        ContinualAnimation.__init__(self, planet, **kwargs)

    def update_mobject(self, dt):
        # time = self.internal_time
        rate = self.rate

        planet = self.planet
        star = self.star
        ellipse = self.ellipse

        rate *= 1 / np.linalg.norm(
            planet.get_center() - star.get_center()
        )
        self.proportion += rate * dt
        self.proportion = self.proportion % 1
        planet.move_to(ellipse.point_from_proportion(self.proportion))


class SunAnimation(ContinualAnimation):
    CONFIG = {
        "rate": 0.2,
        "angle": 60 * DEGREES,
    }

    def __init__(self, sun, **kwargs):
        self.sun = sun
        self.rotated_sun = sun.deepcopy()
        self.rotated_sun.rotate(60 * DEGREES)
        ContinualAnimation.__init__(
            self, Group(sun, self.rotated_sun), **kwargs
        )

    def update_mobject(self, dt):
        time = self.internal_time
        a = (np.sin(self.rate * time * TAU) + 1) / 2.0
        self.rotated_sun.rotate(-self.angle)
        self.rotated_sun.move_to(self.sun)
        self.rotated_sun.rotate(self.angle)
        self.rotated_sun.pixel_array = np.array(
            a * self.sun.pixel_array,
            dtype=self.sun.pixel_array.dtype
        )


class ShowWord(Animation):
    CONFIG = {
        "time_per_char": 0.06,
        "rate_func": None,
    }

    def __init__(self, word, **kwargs):
        assert(isinstance(word, SingleStringTexMobject))
        digest_config(self, kwargs)
        run_time = kwargs.pop(
            "run_time",
            self.time_per_char * len(word)
        )
        self.stroke_width = word.get_stroke_width()
        Animation.__init__(self, word, run_time=run_time, **kwargs)

    def update_mobject(self, alpha):
        word = self.mobject
        stroke_width = self.stroke_width
        count = int(alpha * len(word))
        remainder = (alpha * len(word)) % 1
        word[:count].set_fill(opacity=1)
        word[:count].set_stroke(width=stroke_width)
        if count < len(word):
            word[count].set_fill(opacity=remainder)
            word[count].set_stroke(width=remainder * stroke_width)
            word[count + 1:].set_fill(opacity=0)
            word[count + 1:].set_stroke(width=0)

# Animations


class ShowEmergingEllipse(Scene):
    CONFIG = {
        "circle_radius": 3,
        "circle_color": BLUE,
        "num_lines": 150,
        "lines_stroke_width": 1,
        "eccentricity_vector": 2 * RIGHT,
        "ghost_lines_stroke_color": LIGHT_GREY,
        "ghost_lines_stroke_width": 0.5,
        "ellipse_color": PINK,
    }

    def construct(self):
        circle = self.get_circle()
        e_point = self.get_eccentricity_point()
        e_dot = Dot(e_point, color=YELLOW)
        lines = self.get_lines()
        ellipse = self.get_ellipse()

        fade_rect = FullScreenFadeRectangle()

        line = lines[len(lines) / 5]
        line_dot = Dot(line.get_center(), color=YELLOW)
        line_dot.scale(0.5)

        ghost_line = self.get_ghost_lines(line)
        ghost_lines = self.get_ghost_lines(lines)

        rot_words = TextMobject("Rotate $90^\\circ$ \\\\ about center")
        rot_words.next_to(line_dot, RIGHT)

        elbow = self.get_elbow(line)

        eccentric_words = TextMobject("``Eccentric'' point")
        eccentric_words.next_to(circle.get_center(), DOWN)

        ellipse_words = TextMobject("Perfect ellipse")
        ellipse_words.next_to(ellipse, UP, SMALL_BUFF)

        for text in rot_words, ellipse_words:
            text.add_to_back(text.copy().set_stroke(BLACK, 5))

        shuffled_lines = VGroup(*lines)
        random.shuffle(shuffled_lines.submobjects)

        self.play(ShowCreation(circle))
        self.play(
            FadeInAndShiftFromDirection(e_dot, LEFT),
            Write(eccentric_words, run_time=1)
        )
        self.wait()
        self.play(
            LaggedStart(ShowCreation, shuffled_lines),
            Animation(VGroup(e_dot, circle)),
            FadeOut(eccentric_words)
        )
        self.add(ghost_lines)
        self.add(e_dot, circle)
        self.wait()
        self.play(
            FadeIn(fade_rect),
            Animation(line),
            GrowFromCenter(line_dot),
            FadeInFromDown(rot_words),
        )
        self.wait()
        self.add(ghost_line)
        self.play(
            MoveToTarget(line, path_arc=90 * DEGREES),
            Animation(rot_words),
            ShowCreation(elbow)
        )
        self.wait()
        self.play(
            FadeOut(fade_rect),
            FadeOut(line_dot),
            FadeOut(rot_words),
            FadeOut(elbow),
            Animation(line),
            Animation(ghost_line)
        )
        self.play(
            LaggedStart(MoveToTarget, lines, run_time=4),
            Animation(VGroup(e_dot, circle))
        )
        self.wait()
        self.play(
            ShowCreation(ellipse),
            FadeInFromDown(ellipse_words)
        )
        self.wait()

    def get_circle(self):
        circle = self.circle = Circle(
            radius=self.circle_radius,
            color=self.circle_color
        )
        return circle

    def get_eccentricity_point(self):
        return self.circle.get_center() + self.eccentricity_vector

    def get_lines(self):
        center = self.circle.get_center()
        radius = self.circle.get_width() / 2
        e_point = self.get_eccentricity_point()
        lines = VGroup(*[
            Line(
                e_point,
                center + rotate_vector(radius * RIGHT, angle)
            )
            for angle in np.linspace(0, TAU, self.num_lines)
        ])
        lines.set_stroke(width=self.lines_stroke_width)
        for line in lines:
            line.generate_target()
            line.target.rotate(90 * DEGREES)
        return lines

    def get_ghost_lines(self, lines):
        return lines.copy().set_stroke(
            color=self.ghost_lines_stroke_color,
            width=self.ghost_lines_stroke_width
        )

    def get_elbow(self, line):
        elbow = VGroup(Line(UP, UL), Line(UL, LEFT))
        elbow.set_stroke(width=1)
        elbow.scale(0.2, about_point=ORIGIN)
        elbow.rotate(
            line.get_angle() - 90 * DEGREES,
            about_point=ORIGIN
        )
        elbow.shift(line.get_center())
        return elbow

    def get_ellipse(self):
        center = self.circle.get_center()
        e_point = self.get_eccentricity_point()
        radius = self.circle.get_width() / 2

        # Ellipse parameters
        a = radius / 2
        c = np.linalg.norm(e_point - center) / 2
        b = np.sqrt(a**2 - c**2)

        result = Circle(radius=b, color=self.ellipse_color)
        result.stretch(a / b, 0)
        result.move_to(Line(center, e_point))
        return result


class FeynmanAndOrbitingPlannetOnEllipseDiagram(ShowEmergingEllipse):
    def construct(self):
        circle = self.get_circle()
        lines = self.get_lines()
        ghost_lines = self.get_ghost_lines(lines)
        for line in lines:
            MoveToTarget(line).update(1)
        ellipse = self.get_ellipse()
        e_dot = Dot(self.get_eccentricity_point())
        e_dot.set_color(YELLOW)

        comet = ImageMobject("earth")
        comet.scale_to_fit_width(0.3)

        feynman = ImageMobject("Feynman")
        feynman.scale_to_fit_height(6)
        feynman.next_to(ORIGIN, LEFT)
        feynman.to_edge(UP)
        feynman_name = TextMobject("Richard Feynman")
        feynman_name.next_to(feynman, DOWN)
        feynman.save_state()
        feynman.shift(2 * DOWN)
        feynman_rect = BackgroundRectangle(
            feynman, fill_opacity=1
        )

        group = VGroup(circle, ghost_lines, lines, e_dot, ellipse)

        self.add(group)
        self.add(Orbiting(comet, e_dot, ellipse))
        self.add_foreground_mobjects(comet)
        self.wait()
        self.play(
            feynman.restore,
            MaintainPositionRelativeTo(feynman_rect, feynman),
            VFadeOut(feynman_rect),
            group.to_edge, RIGHT,
        )
        self.play(Write(feynman_name))
        self.wait()
        self.wait(10)


class FeynmanFame(Scene):
    def construct(self):
        books = VGroup(
            ImageMobject("Feynman_QED_cover"),
            ImageMobject("Surely_Youre_Joking_cover"),
            ImageMobject("Feynman_Lectures_cover"),
        )
        for book in books:
            book.scale_to_fit_height(6)
            book.move_to(FRAME_WIDTH * LEFT / 4)

        feynman_diagram = self.get_feynman_diagram()
        feynman_diagram.next_to(ORIGIN, RIGHT)
        fd_parts = VGroup(*reversed(feynman_diagram.family_members_with_points()))

        # As a physicist
        self.play(self.get_book_intro(books[0]))
        self.play(LaggedStart(
            Write, feynman_diagram,
            run_time=4
        ))
        self.wait()
        self.play(
            self.get_book_intro(books[1]),
            self.get_book_outro(books[0]),
            LaggedStart(
                ApplyMethod, fd_parts,
                lambda m: (m.scale, 0),
                run_time=1
            ),
        )
        self.remove(feynman_diagram)
        self.wait()

        # As a public figure
        safe = SVGMobject(file_name="safe", height=2)
        safe_rect = SurroundingRectangle(safe, buff=0)
        safe_rect.set_stroke(width=0)
        safe_rect.set_fill(DARK_GREY, 1)
        safe.add_to_back(safe_rect)

        bongo = SVGMobject(file_name="bongo")
        bongo.scale_to_fit_height(1)
        bongo.set_color(WHITE)
        bongo.next_to(safe, RIGHT, LARGE_BUFF)

        objects = VGroup(safe, bongo)

        feynman_smile = ImageMobject("Feynman_Los_Alamos")
        feynman_smile.scale_to_fit_height(4)
        feynman_smile.next_to(objects, DOWN)

        VGroup(objects, feynman_smile).next_to(ORIGIN, RIGHT)

        joke = TextMobject(
            "``Science is the belief \\\\ in the ignorance of \\\\ experts.''"
        )
        joke.move_to(objects)

        self.play(LaggedStart(
            DrawBorderThenFill, objects,
            lag_ratio=0.75
        ))
        self.play(self.get_book_intro(feynman_smile))
        self.wait()
        self.play(
            objects.shift, 2 * UP,
            VFadeOut(objects)
        )
        self.play(Write(joke))
        self.wait(2)

        self.play(
            self.get_book_intro(books[2]),
            self.get_book_outro(books[1]),
            LaggedStart(FadeOut, joke, run_time=1),
            ApplyMethod(
                feynman_smile.shift, FRAME_HEIGHT * DOWN,
                remover=True
            )
        )

        # As a teacher
        feynman_teacher = ImageMobject("Feynman_teaching")
        feynman_teacher.scale_to_fit_width(FRAME_WIDTH / 2 - 1)
        feynman_teacher.next_to(ORIGIN, RIGHT)

        self.play(self.get_book_intro(feynman_teacher))
        self.wait(3)

    def get_book_animation(self, book,
                           initial_shift,
                           animated_shift,
                           opacity_func
                           ):
        rect = BackgroundRectangle(book, fill_opacity=1)
        book.shift(initial_shift)

        return AnimationGroup(
            ApplyMethod(book.shift, animated_shift),
            UpdateFromAlphaFunc(
                rect, lambda r, a: r.move_to(book).set_fill(
                    opacity=opacity_func(a)
                ),
                remover=True
            )
        )

    def get_book_intro(self, book):
        return self.get_book_animation(
            book, 2 * DOWN, 2 * UP, lambda a: 1 - a
        )

    def get_book_outro(self, book):
        return ApplyMethod(book.shift, FRAME_HEIGHT * UP, remover=True)

    def get_feynman_diagram(self):
        x_min = -1.5
        x_max = 1.5
        arrow = Arrow(LEFT, RIGHT, buff=0, use_rectangular_stem=False)
        arrow.tip.move_to(arrow.get_center())
        arrows = VGroup(*[
            arrow.copy().rotate(angle).next_to(point, vect, buff=0)
            for (angle, point, vect) in [
                (-45 * DEGREES, x_min * RIGHT, UL),
                (-135 * DEGREES, x_min * RIGHT, DL),
                (-135 * DEGREES, x_max * RIGHT, UR),
                (-45 * DEGREES, x_max * RIGHT, DR),
            ]
        ])
        labels = VGroup(*[
            TexMobject(tex)
            for tex in ["e^-", "e^+", "\\text{\\=q}", "q"]
        ])
        vects = [UR, DR, UL, DL]
        for arrow, label, vect in zip(arrows, labels, vects):
            label.next_to(arrow.get_center(), vect, buff=SMALL_BUFF)

        wave = FunctionGraph(
            lambda x: 0.2 * np.sin(2 * TAU * x),
            x_min=x_min,
            x_max=x_max,
        )
        wave_label = TexMobject("\\gamma")
        wave_label.next_to(wave, UP, SMALL_BUFF)
        labels.add(wave_label)

        squiggle = ParametricFunction(
            lambda t: np.array([
                t + 0.5 * np.sin(TAU * t),
                0.5 * np.cos(TAU * t),
                0,
            ]),
            t_min=0,
            t_max=4,
        )
        squiggle.scale(0.25)
        squiggle.set_color(BLUE)
        squiggle.rotate(-30 * DEGREES)
        squiggle.next_to(
            arrows[2].point_from_proportion(0.75),
            DR, buff=0
        )
        squiggle_label = TexMobject("g")
        squiggle_label.next_to(squiggle, UR, buff=-MED_SMALL_BUFF)
        labels.add(squiggle_label)

        return VGroup(arrows, wave, squiggle, labels)


class FeynmanLecturesScreenCaptureFrame(Scene):
    def construct(self):
        url = TextMobject("http://www.feynmanlectures.caltech.edu/")
        url.to_edge(UP)

        screen_rect = ScreenRectangle(height=6)
        screen_rect.next_to(url, DOWN)

        self.add(url)
        self.play(ShowCreation(screen_rect))
        self.wait()


class TheMotionOfPlanets(Scene):
    CONFIG = {
        "camera_config": {"background_opacity": 1},
        "random_seed": 2,
    }

    def construct(self):
        self.add_title()
        self.setup_orbits()

    def add_title(self):
        title = TextMobject("``The motion of planets around the sun''")
        title.set_color(YELLOW)
        title.to_edge(UP)
        title.add_to_back(title.copy().set_stroke(BLACK, 5))
        self.add(title)
        self.title = title

    def setup_orbits(self):
        sun = ImageMobject("sun")
        sun.scale_to_fit_height(0.7)
        planets, ellipses, orbits = self.get_planets_ellipses_and_orbits(sun)

        archivist_words = TextMobject(
            "Judith Goodstein (Caltech archivist)"
        )
        archivist_words.to_corner(UL)
        archivist_words.shift(1.5 * DOWN)
        archivist_words.add_background_rectangle()
        alt_name = TextMobject("David Goodstein (Caltech physicist)")
        alt_name.next_to(archivist_words, DOWN, aligned_edge=LEFT)
        alt_name.add_background_rectangle()

        book = ImageMobject("Lost_Lecture_cover")
        book.scale_to_fit_height(4)
        book.next_to(alt_name, DOWN)

        self.add(SunAnimation(sun))
        self.add(ellipses, planets)
        self.add(self.title)
        self.add(*orbits)
        self.add_foreground_mobjects(planets)
        self.wait(10)
        self.play(
            VGroup(ellipses, sun).shift, 3 * RIGHT,
            FadeInFromDown(archivist_words),
            Animation(self.title)
        )
        self.add_foreground_mobjects(archivist_words)
        self.wait(3)
        self.play(FadeInFromDown(alt_name))
        self.add_foreground_mobjects(alt_name)
        self.wait()
        self.play(FadeInFromDown(book))
        self.wait(15)

    def get_planets_ellipses_and_orbits(self, sun):
        planets = VGroup(
            ImageMobject("mercury"),
            ImageMobject("venus"),
            ImageMobject("earth"),
            ImageMobject("mars"),
            ImageMobject("comet")
        )
        sizes = [0.383, 0.95, 1.0, 0.532, 0.3]
        orbit_radii = [0.254, 0.475, 0.656, 1.0, 3.0]
        orbit_eccentricies = [0.206, 0.006, 0.0167, 0.0934, 0.967]

        for planet, size in zip(planets, sizes):
            planet.scale_to_fit_height(0.5)
            planet.scale(size)

        ellipses = VGroup(*[
            Circle(radius=r, color=WHITE, stroke_width=1)
            for r in orbit_radii
        ])
        for circle, ec in zip(ellipses, orbit_eccentricies):
            a = circle.get_height() / 2
            c = ec * a
            b = np.sqrt(a**2 - c**2)
            circle.stretch(b / a, 1)
            c = np.sqrt(a**2 - b**2)
            circle.shift(c * RIGHT)
        for circle in ellipses:
            circle.rotate(
                TAU * np.random.random(),
                about_point=ORIGIN
            )

        ellipses.scale(3.5, about_point=ORIGIN)

        orbits = [
            Orbiting(
                planet, sun, circle,
                rate=0.25 * r**(2 / 3)
            )
            for planet, circle, r in zip(planets, ellipses, orbit_radii)
        ]
        orbits[-1].proportion = 0.15
        orbits[-1].rate = 0.5

        return planets, ellipses, orbits


class AskAboutEllipses(TheMotionOfPlanets):
    CONFIG = {
        "camera_config": {"background_opacity": 1},
        "sun_center": ORIGIN,
        "animate_sun": True,
        "a": 3.5,
        "b": 2.0,
        "ellipse_color": WHITE,
        "ellipse_stroke_width": 1,
    }

    def construct(self):
        self.add_title()
        self.add_sun()
        self.add_orbit()
        self.add_focus_lines()
        self.add_force_labels()
        self.comment_on_imperfections()
        self.set_up_differential_equations()

    def add_title(self):
        title = Title("Why are orbits ellipses?")
        self.add(title)
        self.title = title

    def add_sun(self):
        sun = ImageMobject("sun", height=0.5)
        sun.move_to(self.sun_center)
        self.sun = sun
        self.add(sun)
        if self.animate_sun:
            self.add(SunAnimation(sun))

    def add_orbit(self):
        sun = self.sun
        comet = ImageMobject("comet")
        comet.scale_to_fit_height(0.2)
        ellipse = self.get_ellipse()
        orbit = Orbiting(comet, sun, ellipse)

        self.add(ellipse)
        self.add(orbit)

        self.ellipse = ellipse
        self.comet = comet
        self.orbit = orbit

    def add_focus_lines(self):
        f1, f2 = self.focus_points
        comet = self.comet
        lines = VGroup(Line(LEFT, RIGHT), Line(LEFT, RIGHT))
        lines.set_stroke(LIGHT_GREY, 1)

        def update_lines(lines):
            l1, l2 = lines
            P = comet.get_center()
            l1.put_start_and_end_on(f1, P)
            l2.put_start_and_end_on(f2, P)
            return lines

        animation = ContinualUpdateFromFunc(
            lines, update_lines
        )
        self.add(animation)
        self.wait(8)

        self.focus_lines = lines
        self.focus_lines_animation = animation

    def add_force_labels(self):
        radial_line = self.focus_lines[0]

        # Radial line measurement
        radius_measurement_kwargs = {
            "num_decimal_places": 3,
            "color": BLUE,
        }
        radius_measurement = DecimalNumber(1, **radius_measurement_kwargs)

        def update_radial_measurement(measurement):
            angle = -radial_line.get_angle() + np.pi
            radial_line.rotate(angle, about_point=ORIGIN)
            new_decimal = DecimalNumber(
                radial_line.get_length(),
                **radius_measurement_kwargs
            )
            max_width = 0.6 * radial_line.get_width()
            if new_decimal.get_width() > max_width:
                new_decimal.scale_to_fit_width(max_width)
            new_decimal.next_to(radial_line, UP, SMALL_BUFF)
            VGroup(new_decimal, radial_line).rotate(
                -angle, about_point=ORIGIN
            )
            Transform(measurement, new_decimal).update(1)

        radius_measurement_animation = ContinualUpdateFromFunc(
            radius_measurement, update_radial_measurement
        )

        # Force equation
        force_equation = TexMobject(
            "F = {GMm \\over (0.000)^2}",
            tex_to_color_map={
                "F": YELLOW,
                "0.000": BLACK,
            }
        )
        force_equation.next_to(self.title, DOWN)
        force_equation.to_edge(RIGHT)
        radius_in_denominator_ref = force_equation.get_part_by_tex("0.000")
        radius_in_denominator = DecimalNumber(
            0, **radius_measurement_kwargs
        )
        radius_in_denominator.scale(0.95)
        update_radius_in_denominator = ContinualChangingDecimal(
            radius_in_denominator,
            lambda a: radial_line.get_length(),
            position_update_func=lambda mob: mob.move_to(
                radius_in_denominator_ref, LEFT
            )
        )

        # Force arrow
        force_arrow = Arrow(LEFT, RIGHT, color=YELLOW)

        def update_force_arrow(arrow):
            radius = radial_line.get_length()
            # target_length = 1 / radius**2
            target_length = 1 / radius  # Lies!
            arrow.scale(
                target_length / arrow.get_length()
            )
            arrow.rotate(
                np.pi + radial_line.get_angle() - arrow.get_angle()
            )
            arrow.shift(
                radial_line.get_end() - arrow.get_start()
            )
        force_arrow_animation = ContinualUpdateFromFunc(
            force_arrow, update_force_arrow
        )

        inverse_square_law_words = TextMobject(
            "``Inverse square law''"
        )
        inverse_square_law_words.next_to(force_equation, DOWN, MED_LARGE_BUFF)
        inverse_square_law_words.to_edge(RIGHT)
        force_equation.next_to(inverse_square_law_words, UP, MED_LARGE_BUFF)

        def v_fade_in(mobject):
            return UpdateFromAlphaFunc(
                mobject,
                lambda mob, alpha: mob.set_fill(opacity=alpha)
            )

        self.add(update_radius_in_denominator)
        self.add(radius_measurement_animation)
        self.play(
            FadeIn(force_equation),
            v_fade_in(radius_in_denominator),
            v_fade_in(radius_measurement)
        )
        self.add(force_arrow_animation)
        self.play(v_fade_in(force_arrow))
        self.wait(8)
        self.play(Write(inverse_square_law_words))
        self.wait(9)

        self.force_equation = force_equation
        self.inverse_square_law_words = inverse_square_law_words
        self.force_arrow = force_arrow
        self.radius_measurement = radius_measurement

    def comment_on_imperfections(self):
        planets, ellipses, orbits = self.get_planets_ellipses_and_orbits(self.sun)
        orbits.pop(-1)
        ellipses.submobjects.pop(-1)
        planets.submobjects.pop(-1)

        scale_factor = 20
        center = self.sun.get_center()
        ellipses.save_state()
        ellipses.scale(scale_factor, about_point=center)

        self.add(*orbits)
        self.play(ellipses.restore, Animation(planets))
        self.wait(7)
        self.play(
            ellipses.scale, scale_factor, {"about_point": center},
            Animation(planets)
        )
        self.remove(*orbits)
        self.remove(planets, ellipses)
        self.wait(2)

    def set_up_differential_equations(self):
        d_dt = TexMobject("{d \\over dt}")
        in_vect = Matrix(np.array([
            "x(t)",
            "y(t)",
            "\\dot{x}(t)",
            "\\dot{y}(t)",
        ]))
        equals = TexMobject("=")
        out_vect = Matrix(np.array([
            "\\dot{x}(t)",
            "\\dot{y}(t)",
            "-x(t) / (x(t)^2 + y(t)^2)^{3/2}",
            "-y(t) / (x(t)^2 + y(t)^2)^{3/2}",
        ]), element_alignment_corner=ORIGIN)

        equation = VGroup(d_dt, in_vect, equals, out_vect)
        equation.arrange_submobjects(RIGHT, buff=SMALL_BUFF)
        equation.scale_to_fit_width(6)

        equation.to_corner(DR, buff=MED_LARGE_BUFF)
        cross = Cross(equation)

        self.play(Write(equation))
        self.wait(6)
        self.play(ShowCreation(cross))
        self.wait(6)

    # Helpers
    def get_ellipse(self):
        a = self.a
        b = self.b
        c = np.sqrt(a**2 - b**2)
        ellipse = Circle(radius=a)
        ellipse.set_stroke(
            self.ellipse_color,
            self.ellipse_stroke_width,
        )
        ellipse.stretch(fdiv(b, a), dim=1)
        ellipse.move_to(
            self.sun.get_center() + c * LEFT / 2
        )
        self.focus_points = [
            self.sun.get_center(),
            self.sun.get_center() + c * LEFT,
        ]
        return ellipse


class FeynmanElementaryQuote(Scene):
    def construct(self):
        quote_text = """
            \\large
            I am going to give what I will call an
            \\emph{elementary} demonstration.  But elementary
            does not mean easy to understand.  Elementary
            means that very little is required
            to know ahead of time in order to understand it,
            except to have an infinite amount of intelligence.
        """
        quote_parts = filter(lambda s: s, quote_text.split(" "))
        quote = TextMobject(
            *quote_parts,
            tex_to_color_map={
                "\\emph{elementary}": BLUE,
                "elementary": BLUE,
                "Elementary": BLUE,
                "infinite": YELLOW,
                "amount": YELLOW,
                "of": YELLOW,
                "intelligence": YELLOW,
                "very": RED,
                "little": RED,
            },
            alignment=""
        )
        quote[-1].shift(2 * SMALL_BUFF * LEFT)
        quote.scale_to_fit_width(FRAME_WIDTH - 1)
        quote.to_edge(UP)
        quote.get_part_by_tex("of").set_color(WHITE)

        nothing = TextMobject("nothing")
        nothing.scale(0.9)
        very = quote.get_part_by_tex("very")
        nothing.shift(very[0].get_left() - nothing[0].get_left())
        nothing.set_color(RED)

        for word in quote:
            if word is very:
                self.add_foreground_mobjects(nothing)
                self.play(ShowWord(nothing))
                self.wait(0.2)
                nothing.sort_submobjects(lambda p: -p[0])
                self.play(LaggedStart(
                    FadeOut, nothing,
                    run_time=1
                ))
                self.remove_foreground_mobject(nothing)
            back_word = word.copy().set_stroke(BLACK, 5)
            self.add_foreground_mobjects(back_word, word)
            self.play(
                ShowWord(back_word),
                ShowWord(word),
            )
            self.wait(0.005 * len(word)**1.5)


class LostLecturePicture(TODOStub):
    CONFIG = {"camera_config": {"background_opacity": 1}}

    def construct(self):
        picture = ImageMobject("Feynman_teaching")
        picture.scale_to_fit_height(FRAME_WIDTH)
        picture.to_corner(UL, buff=0)
        picture.fade(0.5)

        self.play(
            picture.to_corner, DR, {"buff": 0},
            picture.shift, 1.5 * DOWN,
            path_arc=60 * DEGREES,
            run_time=20,
            rate_func=bezier([0, 0, 1, 1])
        )


class AskAboutInfiniteIntelligence(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Infinite intelligence?",
            target_mode="confused"
        )
        self.play(
            self.get_student_changes("horrified", "confused", "sad"),
            self.teacher.change, "happy",
        )
        self.wait()
        self.teacher_says(
            "It's not too bad, \\\\ but stay focused",
            added_anims=[self.get_student_changes(*["happy"] * 3)]
        )
        self.wait()
        self.look_at(self.screen)
        self.wait(5)


class ShowEllipseDefiningProperty(Scene):
    CONFIG = {
        "camera_config": {"background_opacity": 1},
        "ellipse_color": BLUE,
        "a": 4.0,
        "b": 3.0,
        "distance_labels_scale_factor": 1.0,
    }

    def construct(self):
        self.add_ellipse()
        self.add_focal_lines()
        self.add_distance_labels()
        self.label_foci()
        self.label_focal_sum()

    def add_ellipse(self):
        a = self.a
        b = self.b
        ellipse = Circle(radius=a, color=self.ellipse_color)
        ellipse.stretch(fdiv(b, a), dim=1)
        ellipse.to_edge(LEFT, buff=LARGE_BUFF)
        self.ellipse = ellipse
        self.add(ellipse)

    def add_focal_lines(self):
        push_pins = VGroup(*[
            SVGMobject(
                file_name="push_pin",
                color=LIGHT_GREY,
                fill_opacity=0.8,
                height=0.5,
            ).move_to(point, DR).shift(0.05 * RIGHT)
            for point in self.get_foci()
        ])

        dot = Dot()
        dot.scale(0.5)
        position_tracker = ValueTracker(0.125)
        dot_update = ContinualUpdateFromFunc(
            dot,
            lambda d: d.move_to(
                self.ellipse.point_from_proportion(
                    position_tracker.get_value() % 1
                )
            )
        )
        position_tracker_wander = ContinualMovement(
            position_tracker, rate=0.05,
        )

        lines, lines_update_animation = self.get_focal_lines_and_update(
            self.get_foci, dot
        )

        self.add_foreground_mobjects(push_pins, dot)
        self.add(dot_update)
        self.play(LaggedStart(
            FadeInAndShiftFromDirection, push_pins,
            lambda m: (m, 2 * UP + LEFT),
            run_time=1,
            lag_ratio=0.75
        ))
        self.play(ShowCreation(lines))
        self.add(lines_update_animation)
        self.add(position_tracker_wander)
        self.wait(2)

        self.position_tracker = position_tracker
        self.focal_lines = lines

    def add_distance_labels(self):
        lines = self.focal_lines
        colors = [YELLOW, PINK]

        distance_labels, distance_labels_animation = \
            self.get_distance_labels_and_update(lines, colors)

        sum_expression, numbers, number_updates = \
            self.get_sum_expression_and_update(
                lines, colors, lambda mob: mob.to_corner(UR)
            )

        sum_expression_fading_rect = BackgroundRectangle(
            sum_expression, fill_opacity=1
        )

        sum_rect = SurroundingRectangle(numbers[-1])
        constant_words = TextMobject("Stays constant")
        constant_words.next_to(sum_rect, DOWN, aligned_edge=RIGHT)
        VGroup(sum_rect, constant_words).set_color(BLUE)

        self.add(distance_labels_animation)
        self.add(*number_updates)
        self.add(sum_expression)
        self.add_foreground_mobjects(sum_expression_fading_rect)
        self.play(
            VFadeIn(distance_labels),
            FadeOut(sum_expression_fading_rect),
        )
        self.remove_foreground_mobject(sum_expression_fading_rect)
        self.wait(7)
        self.play(
            ShowCreation(sum_rect),
            Write(constant_words)
        )
        self.wait(7)
        self.play(FadeOut(sum_rect), FadeOut(constant_words))

        self.sum_expression = sum_expression
        self.sum_rect = sum_rect

    def label_foci(self):
        foci = self.get_foci()
        focus_words = VGroup(*[
            TextMobject("Focus").next_to(focus, DOWN)
            for focus in foci
        ])
        foci_word = TextMobject("Foci")
        foci_word.move_to(focus_words)
        foci_word.shift(MED_SMALL_BUFF * UP)
        connecting_lines = VGroup(*[
            Arrow(
                foci_word.get_edge_center(-edge),
                focus_word.get_edge_center(edge),
                buff=MED_SMALL_BUFF,
                stroke_width=2,
            )
            for focus_word, edge in zip(focus_words, [LEFT, RIGHT])
        ])

        translation = TextMobject(
            "``Foco'' $\\rightarrow$ Fireplace"
        )
        translation.to_edge(RIGHT)
        translation.shift(UP)
        sun = ImageMobject("sun", height=0.5)
        sun.move_to(foci[0])
        sun_animation = SunAnimation(sun)

        self.play(FadeInFromDown(focus_words))
        self.wait(2)
        self.play(
            ReplacementTransform(focus_words.copy(), foci_word),
        )
        self.play(*map(ShowCreation, connecting_lines))
        for word in list(focus_words) + [foci_word]:
            word.add_background_rectangle()
            self.add_foreground_mobjects(word)
        self.wait(4)
        self.play(Write(translation))
        self.wait(2)
        self.play(GrowFromCenter(sun))
        self.add(sun_animation)
        self.wait(8)

    def label_focal_sum(self):
        sum_rect = self.sum_rect

        focal_sum = TextMobject("``Focal sum''")
        focal_sum.scale(1.5)
        focal_sum.next_to(sum_rect, DOWN, aligned_edge=RIGHT)
        VGroup(sum_rect, focal_sum).set_color(RED)

        footnote = TextMobject(
            """
            \\Large
            *This happens to equal the longest distance
            across the ellipse, so perhaps the more standard
            terminology would be ``major axis'', but I want
            some terminology that conveys the idea of adding
            two distances to the foci.
            """,
            alignment="",
        )
        footnote.scale_to_fit_width(5)
        footnote.to_corner(DR)
        footnote.set_stroke(WHITE, 0.5)

        self.play(FadeInFromDown(focal_sum))
        self.play(Write(sum_rect))
        self.wait()
        self.play(FadeIn(footnote))
        self.wait(2)
        self.play(FadeOut(footnote))
        self.wait(8)

    # Helpers
    def get_foci(self):
        ellipse = self.ellipse
        a = ellipse.get_width() / 2
        b = ellipse.get_height() / 2
        c = np.sqrt(a**2 - b**2)
        center = ellipse.get_center()
        return [
            center + c * RIGHT,
            center + c * LEFT,
        ]

    def get_focal_lines_and_update(self, get_foci, focal_sum_point):
        lines = VGroup(Line(LEFT, RIGHT), Line(LEFT, RIGHT))
        lines.set_stroke(width=2)

        def update_lines(lines):
            foci = get_foci()
            for line, focus in zip(lines, foci):
                line.put_start_and_end_on(
                    focus, focal_sum_point.get_center()
                )
            lines[1].rotate(np.pi)
        lines_update_animation = ContinualUpdateFromFunc(
            lines, update_lines
        )
        return lines, lines_update_animation

    def get_distance_labels_and_update(self, lines, colors):
        distance_labels = VGroup(
            DecimalNumber(0), DecimalNumber(0),
        )
        for label in distance_labels:
            label.scale(self.distance_labels_scale_factor)

        def update_distance_labels(labels):
            for label, line, color in zip(labels, lines, colors):
                angle = -line.get_angle()
                if np.abs(angle) > 90 * DEGREES:
                    angle = 180 * DEGREES + angle
                line.rotate(angle, about_point=ORIGIN)
                new_decimal = DecimalNumber(line.get_length())
                new_decimal.scale(
                    self.distance_labels_scale_factor
                )
                max_width = 0.6 * line.get_width()
                if new_decimal.get_width() > max_width:
                    new_decimal.scale_to_fit_width(max_width)
                new_decimal.next_to(line, UP, SMALL_BUFF)
                new_decimal.set_color(color)
                new_decimal.add_to_back(
                    new_decimal.copy().set_stroke(BLACK, 5)
                )
                VGroup(new_decimal, line).rotate(
                    -angle, about_point=ORIGIN
                )
                label.submobjects = list(new_decimal.submobjects)

        distance_labels_animation = ContinualUpdateFromFunc(
            distance_labels, update_distance_labels
        )

        return distance_labels, distance_labels_animation

    def get_sum_expression_and_update(self, lines, colors, sum_position_func):
        sum_expression = TexMobject("0.00", "+", "0.00", "=", "0.00")
        sum_position_func(sum_expression)
        number_refs = sum_expression.get_parts_by_tex("0.00")
        number_refs.set_fill(opacity=0)
        numbers = VGroup(*[DecimalNumber(0) for ref in number_refs])
        for number, color in zip(numbers, colors):
            number.set_color(color)

        # Not the most elegant...
        number_updates = [
            ContinualChangingDecimal(
                numbers[0], lambda a: lines[0].get_length(),
                position_update_func=lambda m: m.move_to(
                    number_refs[1], LEFT
                )
            ),
            ContinualChangingDecimal(
                numbers[1], lambda a: lines[1].get_length(),
                position_update_func=lambda m: m.move_to(
                    number_refs[0], LEFT
                )
            ),
            ContinualChangingDecimal(
                numbers[2], lambda a: sum(map(Line.get_length, lines)),
                position_update_func=lambda m: m.move_to(
                    number_refs[2], LEFT
                )
            ),
        ]

        return sum_expression, numbers, number_updates


class GeometryProofLand(Scene):
    CONFIG = {
        "colors": [
            PINK, RED, YELLOW, GREEN, GREEN_A, BLUE,
            MAROON_E, MAROON_B, YELLOW, BLUE,
        ],
    }

    def construct(self):
        word = self.get_geometry_proof_land_word()
        word_outlines = word.deepcopy()
        word_outlines.set_fill(opacity=0)
        word_outlines.set_stroke(WHITE, 1)
        colors = list(self.colors)
        random.shuffle(colors)
        word_outlines.set_color_by_gradient(*colors)

        circles = VGroup()
        for letter in word:
            circle = Circle()
            # circle = letter.copy()
            circle.replace(letter, dim_to_match=1)
            circle.scale(3)
            circle.set_stroke(WHITE, 0)
            circle.set_fill(letter.get_color(), 0)
            circles.add(circle)
            circle.target = letter

        self.play(
            LaggedStart(MoveToTarget, circles),
            run_time=2
        )
        self.play(LaggedStart(
            ShowCreationThenDestruction, word_outlines,
            run_time=4
        ))
        self.wait()

    def get_geometry_proof_land_word(self):
        word = TextMobject("Geometry proof land")
        word.rotate(-90 * DEGREES)
        word.scale(0.25)
        word.shift(3 * RIGHT)
        word.apply_complex_function(np.exp)
        word.rotate(90 * DEGREES)
        word.scale_to_fit_width(9)
        word.center()
        word.to_edge(UP)
        word.set_color_by_gradient(*self.colors)
        return word


class ProveEllipse(ShowEmergingEllipse, ShowEllipseDefiningProperty):
    CONFIG = {
        "eccentricity_vector": 1.5 * RIGHT,
        "ellipse_color": PINK,
        "distance_labels_scale_factor": 0.7,
    }

    def construct(self):
        self.setup_ellipse()
        self.hypothesize_foci()
        self.setup_and_show_focal_sum()
        self.show_circle_radius()
        self.limit_to_just_one_line()
        self.look_at_perpendicular_bisector()
        self.show_orbiting_planet()

    def setup_ellipse(self):
        circle = self.circle = self.get_circle()
        circle.to_edge(LEFT)
        ep = self.get_eccentricity_point()
        ep_dot = self.ep_dot = Dot(ep, color=YELLOW)
        lines = self.lines = self.get_lines()
        for line in lines:
            line.save_state()
        ghost_lines = self.ghost_lines = self.get_ghost_lines(lines)
        ellipse = self.ellipse = self.get_ellipse()

        self.add(ghost_lines, circle, lines, ep_dot)
        self.play(
            LaggedStart(MoveToTarget, lines),
            Animation(ep_dot),
        )
        self.play(ShowCreation(ellipse))
        self.wait()

    def hypothesize_foci(self):
        circle = self.circle
        ghost_lines = self.ghost_lines
        ghost_lines_copy = ghost_lines.copy().set_stroke(YELLOW, 3)

        center = circle.get_center()
        center_dot = Dot(center, color=RED)
        # ep = self.get_eccentricity_point()
        ep_dot = self.ep_dot
        dots = VGroup(center_dot, ep_dot)

        center_label = TextMobject("Circle center")
        ep_label = TextMobject("Eccentric point")
        labels = VGroup(center_label, ep_label)
        vects = [UL, DR]
        arrows = VGroup()
        for label, dot, vect in zip(labels, dots, vects):
            label.next_to(dot, vect, MED_LARGE_BUFF)
            label.match_color(dot)
            label.add_to_back(
                label.copy().set_stroke(BLACK, 5)
            )
            arrow = Arrow(
                label.get_corner(-vect),
                dot.get_corner(vect),
                buff=SMALL_BUFF
            )
            arrow.match_color(dot)
            arrow.add_to_back(arrow.copy().set_stroke(BLACK, 5))
            arrows.add(arrow)

        labels_target = labels.copy()
        labels_target.arrange_submobjects(
            DOWN, aligned_edge=LEFT
        )
        guess_start = TextMobject("Guess: Foci = ")
        brace = Brace(labels_target, LEFT)
        full_guess = VGroup(guess_start, brace, labels_target)
        full_guess.arrange_submobjects(RIGHT)
        full_guess.to_corner(UR)

        self.play(
            FadeInFromDown(labels[1]),
            GrowArrow(arrows[1]),
        )
        self.play(LaggedStart(
            ShowPassingFlash, ghost_lines_copy
        ))
        self.wait()
        self.play(ReplacementTransform(circle.copy(), center_dot))
        self.add_foreground_mobjects(dots)
        self.play(
            FadeInFromDown(labels[0]),
            GrowArrow(arrows[0]),
        )
        self.wait()
        self.play(
            Write(guess_start),
            GrowFromCenter(brace),
            run_time=1
        )
        self.play(
            ReplacementTransform(labels.copy(), labels_target)
        )
        self.wait()
        self.play(FadeOut(labels), FadeOut(arrows))

        self.center_dot = center_dot

    def setup_and_show_focal_sum(self):
        circle = self.circle
        ellipse = self.ellipse

        focal_sum_point = VectorizedPoint()
        focal_sum_point.move_to(circle.get_top())
        dots = [self.ep_dot, self.center_dot]
        colors = map(Mobject.get_color, dots)

        def get_foci():
            return map(Mobject.get_center, dots)

        focal_lines, focal_lines_update_animation = \
            self.get_focal_lines_and_update(get_foci, focal_sum_point)
        distance_labels, distance_labels_update_animation = \
            self.get_distance_labels_and_update(focal_lines, colors)
        sum_expression, numbers, number_updates = \
            self.get_sum_expression_and_update(
                focal_lines, colors,
                lambda mob: mob.to_edge(RIGHT).shift(UP)
            )

        to_add = self.focal_sum_things_to_add = [
            focal_lines_update_animation,
            distance_labels_update_animation,
            sum_expression,
        ] + list(number_updates)

        self.play(
            ShowCreation(focal_lines),
            Write(distance_labels),
            FadeIn(sum_expression),
            Write(numbers),
            run_time=1
        )
        self.wait()
        self.add(*to_add)

        points = [
            ellipse.get_top(),
            circle.point_from_proportion(0.2),
            ellipse.point_from_proportion(0.2),
            ellipse.point_from_proportion(0.4),
        ]
        for point in points:
            self.play(
                focal_sum_point.move_to, point
            )
            self.wait()
        self.remove(*to_add)
        self.play(*map(FadeOut, [
            focal_lines, distance_labels,
            sum_expression, numbers
        ]))

        self.set_variables_as_attrs(
            focal_lines, focal_lines_update_animation,
            focal_sum_point,
            distance_labels, distance_labels_update_animation,
            sum_expression,
            numbers, number_updates
        )

    def show_circle_radius(self):
        circle = self.circle
        center = circle.get_center()
        point = circle.get_right()
        color = GREEN
        radius = Line(center, point, color=color)
        radius_measurement = DecimalNumber(radius.get_length())
        radius_measurement.set_color(color)
        radius_measurement.next_to(radius, UP, SMALL_BUFF)
        radius_measurement.add_to_back(
            radius_measurement.copy().set_stroke(BLACK, 5)
        )
        group = VGroup(radius, radius_measurement)
        group.rotate(30 * DEGREES, about_point=center)

        self.play(ShowCreation(radius))
        self.play(Write(radius_measurement))
        self.wait()
        self.play(Rotating(
            group,
            rate_func=smooth,
            run_time=7,
            about_point=center
        ))
        self.play(FadeOut(group))

    def limit_to_just_one_line(self):
        lines = self.lines
        ghost_lines = self.ghost_lines
        ep_dot = self.ep_dot

        index = int(0.2 * len(lines))
        line = lines[index]
        ghost_line = ghost_lines[index]
        to_fade = VGroup(*list(lines) + list(ghost_lines))
        to_fade.remove(line, ghost_line)

        P_dot = Dot(line.saved_state.get_end())
        P_label = TexMobject("P")
        P_label.next_to(P_dot, UP, SMALL_BUFF)

        self.add_foreground_mobjects(self.ellipse)
        self.play(LaggedStart(Restore, lines))
        self.play(
            FadeOut(to_fade),
            line.set_stroke, {"width": 3},
            ReplacementTransform(ep_dot.copy(), P_dot),
        )
        self.play(FadeInFromDown(P_label))
        self.wait()

        for l in lines:
            l.generate_target()
            l.target.rotate(
                90 * DEGREES,
                about_point=l.get_center()
            )

        self.set_variables_as_attrs(
            line, ghost_line,
            P_dot, P_label
        )

    def look_at_perpendicular_bisector(self):
        # Alright, this method's gonna blow up.  Let's go!
        circle = self.circle
        ellipse = self.ellipse
        ellipse.save_state()
        lines = self.lines
        line = self.line
        ghost_lines = self.ghost_lines
        ghost_line = self.ghost_line
        P_dot = self.P_dot
        P_label = self.P_label

        elbow = self.get_elbow(line)
        self.play(
            MoveToTarget(line, path_arc=90 * DEGREES),
            ShowCreation(elbow)
        )

        # Perpendicular bisector label
        label = TextMobject("``Perpendicular bisector''")
        label.scale(0.75)
        label.set_color(YELLOW)
        label.next_to(ORIGIN, UP, MED_SMALL_BUFF)
        label.add_background_rectangle()
        angle = line.get_angle() + np.pi
        label.rotate(angle, about_point=ORIGIN)
        label.shift(line.get_center())

        # Dot defining Q point
        Q_dot = Dot(color=GREEN)
        Q_dot.move_to(self.focal_sum_point)
        focal_sum_point_animation = NormalAnimationAsContinualAnimation(
            MaintainPositionRelativeTo(
                self.focal_sum_point, Q_dot
            )
        )
        self.add(focal_sum_point_animation)
        Q_dot.move_to(line.point_from_proportion(0.9))
        Q_dot.save_state()

        Q_label = TexMobject("Q")
        Q_label.scale(0.7)
        Q_label.match_color(Q_dot)
        Q_label.add_to_back(Q_label.copy().set_stroke(BLACK, 5))
        Q_label.next_to(Q_dot, UL, buff=0)
        Q_label_animation = NormalAnimationAsContinualAnimation(
            MaintainPositionRelativeTo(Q_label, Q_dot)
        )

        # Pretty hacky...
        def distance_label_shift_update(label):
            line = self.focal_lines[0]
            if line.get_end()[0] > line.get_start()[0]:
                vect = label.get_center() - line.get_center()
                label.shift(-2 * vect)
        distance_label_shift_update_animation = ContinualUpdateFromFunc(
            self.distance_labels[0],
            distance_label_shift_update
        )
        self.focal_sum_things_to_add.append(
            distance_label_shift_update_animation
        )

        # Define QP line
        QP_line = Line(LEFT, RIGHT)
        QP_line.match_style(self.focal_lines)
        QP_line_update = ContinualUpdateFromFunc(
            QP_line, lambda l: l.put_start_and_end_on(
                Q_dot.get_center(), P_dot.get_center(),
            )
        )

        QE_line = Line(LEFT, RIGHT)
        QE_line.set_stroke(YELLOW, 3)
        QE_line_update = ContinualUpdateFromFunc(
            QE_line, lambda l: l.put_start_and_end_on(
                Q_dot.get_center(),
                self.get_eccentricity_point()
            )
        )

        # Define similar triangles
        triangles = VGroup(*[
            Polygon(
                Q_dot.get_center(),
                line.get_center(),
                end_point,
                fill_opacity=1,
            )
            for end_point in [
                P_dot.get_center(),
                self.get_eccentricity_point()
            ]
        ])
        triangles.set_color_by_gradient(RED_C, COBALT)
        triangles.set_stroke(WHITE, 2)

        # Add even more distant label updates
        def distance_label_rotate_update(label):
            QE_line_update.update(0)
            angle = QP_line.get_angle() - QE_line.get_angle()
            label.rotate(angle, about_point=Q_dot.get_center())
            return label

        distance_label_rotate_update_animation = ContinualUpdateFromFunc(
            self.distance_labels[0],
            distance_label_rotate_update
        )

        # Hook up line to P to P_dot
        radial_line = DashedLine(ORIGIN, 3 * RIGHT)
        radial_line_update = UpdateFromFunc(
            radial_line, lambda l: l.put_start_and_end_on(
                circle.get_center(),
                P_dot.get_center()
            )
        )

        def put_dot_at_intersection(dot):
            point = line_intersection(
                line.get_start_and_end(),
                radial_line.get_start_and_end()
            )
            dot.move_to(point)
            return dot

        keep_Q_dot_at_intersection = UpdateFromFunc(
            Q_dot, put_dot_at_intersection
        )
        Q_dot.restore()

        ghost_line_update_animation = UpdateFromFunc(
            ghost_line, lambda l: l.put_start_and_end_on(
                self.get_eccentricity_point(),
                P_dot.get_center()
            )
        )

        def update_perp_bisector(line):
            line.scale(ghost_line.get_length() / line.get_length())
            line.rotate(ghost_line.get_angle() - line.get_angle())
            line.rotate(90 * DEGREES)
            line.move_to(ghost_line)
        perp_bisector_update_animation = UpdateFromFunc(
            line, update_perp_bisector
        )
        elbow_update_animation = UpdateFromFunc(
            elbow,
            lambda e: Transform(e, self.get_elbow(ghost_line)).update(1)
        )

        P_dot_movement_updates = [
            radial_line_update,
            keep_Q_dot_at_intersection,
            MaintainPositionRelativeTo(
                P_label, P_dot
            ),
            ghost_line_update_animation,
            perp_bisector_update_animation,
            elbow_update_animation,
        ]

        # Comment for tangency
        sum_rect = SurroundingRectangle(
            self.numbers[-1]
        )
        tangency_comment = TextMobject(
            "Always $\\ge$ radius"
        )
        tangency_comment.next_to(
            sum_rect, DOWN,
            aligned_edge=RIGHT
        )
        VGroup(sum_rect, tangency_comment).set_color(GREEN)

        # Why is this needed?!?
        self.add(*self.focal_sum_things_to_add)
        self.wait(0.01)
        self.remove(*self.focal_sum_things_to_add)

        # Show label
        self.play(Write(label))
        self.wait()

        # Show Q_dot moving about a little
        self.play(
            FadeOut(label),
            FadeIn(self.focal_lines),
            FadeIn(self.distance_labels),
            FadeIn(self.sum_expression),
            FadeIn(self.numbers),
            ellipse.set_stroke, {"width": 0.5},
        )
        self.add(*self.focal_sum_things_to_add)
        self.play(
            FadeInFromDown(Q_label),
            GrowFromCenter(Q_dot)
        )
        self.wait()
        self.add_foreground_mobjects(Q_dot)
        self.add(Q_label_animation)
        self.play(
            Q_dot.move_to, line.point_from_proportion(0.05),
            rate_func=there_and_back,
            run_time=4
        )
        self.wait()

        # Show similar triangles
        self.play(
            FadeIn(triangles[0]),
            ShowCreation(QP_line),
            Animation(elbow),
        )
        self.add(QP_line_update)
        for i in range(3):
            self.play(
                FadeIn(triangles[(i + 1) % 2]),
                FadeOut(triangles[i % 2]),
                Animation(self.distance_labels),
                Animation(elbow)
            )
        self.play(
            FadeOut(triangles[1]),
            Animation(self.distance_labels)
        )

        # Move first distance label
        # (boy, this got messy...hopefully no one ever has
        # to read this.)
        angle = QP_line.get_angle() - QE_line.get_angle()
        Q_point = Q_dot.get_center()
        for x in range(2):
            self.play(ShowCreationThenDestruction(QE_line))
        distance_label_copy = self.distance_labels[0].copy()
        self.play(
            ApplyFunction(
                distance_label_rotate_update,
                distance_label_copy,
                path_arc=angle
            ),
            Rotate(QE_line, angle, about_point=Q_point)
        )
        self.play(FadeOut(QE_line))
        self.remove(distance_label_copy)
        self.add(distance_label_rotate_update_animation)
        self.focal_sum_things_to_add.append(
            distance_label_rotate_update_animation
        )
        self.wait()
        self.play(
            Q_dot.move_to, line.point_from_proportion(0),
            run_time=4,
            rate_func=there_and_back
        )

        # Trace out ellipse
        self.play(ShowCreation(radial_line))
        self.wait()
        self.play(
            ApplyFunction(put_dot_at_intersection, Q_dot),
            run_time=3,
        )
        self.wait()
        self.play(
            Rotating(
                P_dot,
                about_point=circle.get_center(),
                rate_func=bezier([0, 0, 1, 1]),
                run_time=10,
            ),
            ellipse.restore,
            *P_dot_movement_updates
        )
        self.wait()

        # Talk through tangency
        self.play(
            ShowCreation(sum_rect),
            Write(tangency_comment),
        )
        points = [line.get_end(), line.get_start(), Q_dot.get_center()]
        run_times = [1, 3, 2]
        for point, run_time in zip(points, run_times):
            self.play(Q_dot.move_to, point, run_time=run_time)
        self.wait()

        self.remove(*self.focal_sum_things_to_add)
        self.play(*map(FadeOut, [
            radial_line,
            QP_line,
            P_dot, P_label,
            Q_dot, Q_label,
            elbow,
            self.distance_labels,
            self.numbers,
            self.sum_expression,
            sum_rect,
            tangency_comment,
        ]))
        self.wait()

        # Show all lines
        lines.remove(line)
        ghost_lines.remove(ghost_line)
        for line in lines:
            line.generate_target()
            line.target.rotate(90 * DEGREES)
        self.play(
            LaggedStart(FadeIn, ghost_lines),
            LaggedStart(FadeIn, lines),
        )
        self.play(LaggedStart(MoveToTarget, lines))
        self.wait()

    def show_orbiting_planet(self):
        ellipse = self.ellipse
        ep_dot = self.ep_dot
        planet = ImageMobject("earth")
        planet.scale_to_fit_height(0.25)
        orbit = Orbiting(planet, ep_dot, ellipse)

        lines = self.lines

        def update_lines(lines):
            for gl, line in zip(self.ghost_lines, lines):
                intersection = line_intersection(
                    [self.circle.get_center(), gl.get_end()],
                    line.get_start_and_end()
                )
                distance = np.linalg.norm(
                    intersection - planet.get_center()
                )
                if distance < 0.025:
                    line.set_stroke(BLUE, 3)
                    self.add(line)
                else:
                    line.set_stroke(WHITE, 1)

        lines_update_animation = ContinualUpdateFromFunc(
            lines, update_lines
        )

        self.add(orbit)
        self.add(lines_update_animation)
        self.add_foreground_mobjects(planet)
        self.wait(12)


class EndOfGeometryProofiness(GeometryProofLand):
    def construct(self):
        geometry_word = self.get_geometry_proof_land_word()
        orbital_mechanics = TextMobject("Orbital Mechanics")
        orbital_mechanics.scale(1.5)
        orbital_mechanics.to_edge(UP)
        underline = Line(LEFT, RIGHT)
        underline.match_width(orbital_mechanics)
        underline.next_to(orbital_mechanics, DOWN, SMALL_BUFF)

        self.play(LaggedStart(FadeOutAndShiftDown, geometry_word))
        self.play(FadeInFromDown(orbital_mechanics))
        self.play(ShowCreation(underline))
        self.wait()


class KeplersSecondLaw(AskAboutEllipses):
    CONFIG = {
        "sun_center": 3 * RIGHT + DOWN,
        "animate_sun": False,
        "a": 5.0,
        "b": 2.5,
        "ellipse_stroke_width": 2,
        "area_color": COBALT,
        "area_opacity": 0.75,
        "arc_color": YELLOW,
        "arc_stroke_width": 3,
    }

    def construct(self):
        self.add_title()
        self.add_sun()
        self.add_foreground_mobjects(self.sun)
        self.add_orbit()
        self.add_foreground_mobjects(self.comet)

        self.show_several_sweeps()
        self.contrast_close_to_far()


    def add_title(self):
        title = TextMobject("Kepler's 2nd law")
        title.scale(1.0)
        title.to_edge(UP)
        self.add(title)
        self.title = title

    def show_several_sweeps(self):
        n_sweeps = 3
        shown_areas = VGroup()
        for x in range(n_sweeps):
            self.wait()
            area = self.show_area_sweep()
            shown_areas.add(area)
        self.wait(2)
        self.play(FadeOut(shown_areas))


    def contrast_close_to_far(self):
        orbit = self.orbit
        sun_point = self.sun.get_center()

        start_prop = 0.8
        self.wait_until_proportion(start_prop)
        area = self.show_area_sweep()
        end_prop = max(0.9, orbit.proportion)
        arc = self.get_arc(start_prop, end_prop)
        radius = Line(sun_point, arc.points[0])
        radius.set_color(PINK)


        radius_words = self.get_radius_words(
            radius, "Short"
        )

        arc_words = TextMobject("Long arc")
        angle = 9 * DEGREES
        arc_words.rotate(angle)
        arc_words.scale(0.1)
        vect = rotate_vector(RIGHT, angle)
        arc_words.next_to(vect, vect)
        arc_words.apply_complex_function(np.exp)
        arc_words.scale(2)
        arc_words.next_to(
            arc.point_from_proportion(0.5),
            rotate_vector(vect, 90 * DEGREES),
            buff=-MED_SMALL_BUFF,
        )
        arc_words.match_color(arc)

        # Show stubby arc
        # self.remove(orbit)
        # self.add(self.comet)
        self.play(
            ShowCreation(radius),
            Write(radius_words),
        )
        self.play(
            ShowCreation(arc),
            Write(arc_words)
        )

        # Show narrow arc
        # (Code repetition...uck)
        start_prop = 0.4
        self.wait_until_proportion(start_prop)
        area = self.show_area_sweep()
        end_prop = max(0.45, orbit.proportion)
        arc = self.get_arc(start_prop, end_prop)
        radius = Line(sun_point, arc.points[0])
        radius.set_color(PINK)
        radius_words = self.get_radius_words(radius, "Long")

    # Helpers
    def show_area_sweep(self, time=1.0):
        orbit = self.orbit
        start_prop = orbit.proportion
        area = self.get_area(start_prop, start_prop)
        area_update = UpdateFromFunc(
            area,
            lambda a: Transform(
                a, self.get_area(start_prop, orbit.proportion)
            ).update(1)
        )

        self.play(area_update, run_time=time)

        return area

    def get_area(self, prop1, prop2):
        """
        Return a mobject illustrating the area swept
        out between a point prop1 of the way along
        the ellipse, and prop2 of the way.
        """
        sun_point = self.sun.get_center()
        arc = self.get_arc(prop1, prop2)

        # Add lines from start
        result = VMobject()
        result.append_vectorized_mobject(
            Line(sun_point, arc.points[0])
        )
        result.append_vectorized_mobject(arc)
        result.append_vectorized_mobject(
            Line(arc.points[-1], sun_point)
        )

        result.set_stroke(WHITE, width=0)
        result.set_fill(
            self.area_color,
            self.area_opacity,
        )
        return result

    def get_arc(self, prop1, prop2):
        sun_point = self.sun.get_center()
        ellipse = self.get_ellipse()
        prop1 = prop1 % 1.0
        prop2 = prop2 % 1.0

        if prop2 > prop1:
            arc = VMobject().pointwise_become_partial(
                ellipse, prop1, prop2
            )
        elif prop1 > prop2:
            arc, arc_extension = [
                VMobject().pointwise_become_partial(
                    ellipse, p1, p2
                )
                for p1, p2 in [(prop1, 1.0), (0.0, prop2)]
            ]
            arc.append_vectorized_mobject(arc_extension)
        else:
            arc = VectorizedPoint(
                ellipse.point_from_proportion(prop1)
            )

        arc.set_stroke(
            self.arc_color,
            self.arc_stroke_width,
        )

        return arc

    def wait_until_proportion(self, prop):
        if self.skip_animations:
            self.orbit.proportion = prop
        else:
            while self.orbit.proportion < prop:
                self.wait(0.2)

    def get_radius_words(self, radius, adjective):
        radius_words = TextMobject(
            "%s radius" % adjective,
        )
        radius_words.scale_to_fit_width(
            0.8 * radius.get_length()
        )
        radius_words.match_color(radius)
        radius_words.next_to(ORIGIN, DOWN, SMALL_BUFF)
        radius_words.rotate(radius.get_angle(), about_point=ORIGIN)
        radius_words.shift(radius.get_center())
        return radius_words
