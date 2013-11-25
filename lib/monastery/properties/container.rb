require_relative 'property.rb'

def move(thing, where)
    thing.move(where)
end

class Thing
    def move(where)
        self.make Location if self.not? Location
        self.location.place = where
    end
end

module Properties
    class Location < Property
        attr_accessor :place

        def unmake
            place.contents.delete(owner) if not place.nil?
        end

        def place=(where)
            if not place.nil? then
                place.owner.call(:removed, self)
                self.owner.call(:removed_from, place)
                place.contents.delete(owner)
            end
            @place = where
            if not place.nil? then
                place.contents << owner
                place.owner.call(:added, self)
                owner.call(:added_to, place)
            end
        end
    end

    class Place < Property
        attr_accessor :contents
        class_attribute :description_verb

        self.description_verb = "contains"

        def initialize
            @contents = []
        end

        def add(thing)
            thing.location.place = self
        end

        def describe
            start = "#{owner.name} #{description_verb}:" 
            start += contents.map(&:name).join(", ")
        end
    end
end
