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
        class_attribute :location_description

        def place(where)
            @place
        end

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
        class_attribute :description_verb

        self.description_verb = "contains"

        def initialize
            @things_present = []
        end

        def add(thing)
            thing.location.place = self
        end

        def describe
            start = "#{self.owner.name} #{self.description_verb}:" 
            start += self.things_present.map(&:name).join(", ")
        end
    end
end
