require_relative 'properties.rb'

module Things
    class Thing
    end
end

module Properties
    class Container < Property
        attr_accessor :contents

        def initialize
            self.contents = []
        end

        def add(thing)
            self.contents << thing
            thing.call(:added, thing, self.owner)
            self.owner.call(:added, thing, self.owner)
        end
    end
end
