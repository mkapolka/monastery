require_relative 'property.rb'

def move(thing, where)
    thing.location.place = where
end

class Thing
    def move(where)
        self.location.place = where
    end
end

module Properties
    class Location < Property
        attr_accessor :place

        def place=(where)
            if not @place.nil? then
                @place.owner.call(:removed, self)
                self.owner.call(:removed_from, @place)
            end
            @place = where
            if not place.nil? then
                @place.owner.call(:added, self)
                owner.call(:added_to, @place)
            end
        end
    end

    class Place < Property
        attr_accessor :things_present

        def add(thing)
            thing.location.place = self
        end
    end
end
