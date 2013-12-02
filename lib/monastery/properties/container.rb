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

        def cease
            self.place = nil
            super
        end

        def place=(where)
            if not place.nil? then
                place.owner.call(Removed, self)
                owner.call(RemovedFrom, place)
                place.contents.delete(owner)
            end
            @place = where
            if not place.nil? then
                place.contents << owner
                place.owner.call(Added, self)
                owner.call(AddedTo, place)
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

        def tick
            contents.each{|c| c.call :tick}
        end

        def describe
            start = "#{owner.name} #{description_verb}:" 
            start += contents.map(&:name).join(", ")
        end
    end

    #A place located inside of an object
    class Container < Place
        def tick
            super
            contents.each_with_index do |thing, index|
                contents[index..-1].each do |other_thing|
                    thing.call(Touch, other_thing)
                    other_thing.call(Touch, thing)
                end
            end
        end
    end
end
