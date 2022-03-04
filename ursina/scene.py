import sys
from panda3d.core import NodePath
from panda3d.core import Fog
from ursina import color
from ursina.texture_importer import load_texture
# from ursina.ursinastuff import destroy
# from ursina.entity import Entity


class Scene(NodePath):

    def __init__(self):
        super().__init__('scene')
        self.render = None
        self.world = None

        self.camera = None
        self.ui_camera = None

        self._entities = []
        self._needs_to_sort_callables = False
        self._callables = {'update' : [], 'input' : [], 'keystroke' : []}
        self.hidden = NodePath('hidden')
        self.reflection_map_name = 'reflection_map_3'


    def set_up(self):
        from ursina.entity import Entity
        self.reparent_to(render)
        self.reflection_map = load_texture(self.reflection_map_name)
        self.fog = Fog('fog')
        self.setFog(self.fog)
        self.fog_color = color.light_gray
        self.fog_density = 0


    def clear(self):
        from ursina.ursinastuff import destroy
        to_destroy = [e for e in self.entities if not e.eternal]
        to_keep = [e for e in self.entities if e.eternal]

        for d in to_destroy:
            try:
                print('destroying:', d.name)
                destroy(d)
            except Exception as e:
                print('failed to destroy entity', e)


        self.entities = to_keep

        from ursina import application
        application.sequences.clear()


    @property
    def entities(self):
        return self._entities

    @entities.setter
    def entities(self, value):
        self._entities = value

        for v in self.callables.values():
            v.clear()

        for e in self.entities:
            self.append_all_callables(e)
            for s in e.scripts:
                self.append_all_callables(s)

    @property
    def callables(self):
        if self._needs_to_sort_callables:
            for v in self._callables.values():
                v.sort(key = lambda e: e.priority if hasattr(e, 'priority') else 0)
            self._needs_to_sort_callables = False
            
        return self._callables

    def append_callable(self, target, entity):
        if entity not in self.callables[target]:
            self.callables[target].append(entity)
            self._needs_to_sort_callables = True
    
    def remove_callable(self, target, entity):
        if entity in self.callables[target]:
            self.callables[target].remove(entity)

    def append_all_callables(self, entity):
        for k,v in self.callables.items():
            if hasattr(entity, k) and entity not in v:
                v.append(entity) 
                self._needs_to_sort_callables = True

    def remove_all_callables(self, entity):
        for v in self.callables.values():
            if entity in v:
                v.remove(entity)

    @property
    def fog_color(self):
        return self.fog.getColor()

    @fog_color.setter
    def fog_color(self, value):
        self.fog.setColor(value)


    @property
    def fog_density(self):
        return self._fog_density

    @fog_density.setter     # set to a number for exponential density or (start, end) for linear.
    def fog_density(self, value):
        self._fog_density = value
        if isinstance(value, tuple):     # linear fog
            self.fog.setLinearRange(value[0], value[1])
        else:
            self.fog.setExpDensity(value)


instance = Scene()



if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    # yolo = Button(name='yolo', text='yolo')
    e = Entity(model='plane', color=color.black, scale=100)
    EditorCamera()
    s = Sky()

    def input(key):
        if key == 'l':
            for e in scene.entities:
                print(e.name)

        if key == 'd':
            scene.clear()

    scene.fog_density = .1          # sets exponential density
    scene.fog_density = (50, 200)   # sets linear density start and end

    app.run()
