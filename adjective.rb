class Adjective
   attr_accessor :count, :value, :noun

   class << self
      attr_reader :events, :types
   end

   def initialize
      @count = 0;
   end

   def inspect
      return self;
   end

   def describe()
      return ""
   end

   def self.description(string)
      self.class_eval do 
         define_method(:describe) do
            string
         end
      end
   end

   def self.upon(event, &block)
      self.class_eval do
         @events ||= {};
         @events[event] = block;
      end
   end

   def self.types(*args)
      return @types if args.length==0
      @types ||= [];
      args.each do |x|
         @types.push(x) if @types.index(x).nil?
      end
   end

   def types
      self.class.class_eval do
         @types
      end
   end
end

module Adjectives
   def self.adjective(name, options={}, &block)
      cnew = Class.new(Adjective);
      cnew.instance_eval(&block)
      Adjectives.const_set(name.to_s.capitalize, cnew)
   end

   def self.the_following_are(*new_types, &block)
      old_adjectives = Adjectives.constants;
      yield
      new_adjectives = Adjectives.constants - old_adjectives;
      new_adjectives.each do |x|
         Adjectives.const_get(x).types new_types
      end
   end

   class Fuzzy < Adjective
      description "is fuzzy"
      types :physical
   end

   the_following_are :physical do
      class Hard < Adjective
         description "is hard"

         def bash(basher)
            puts "Rings like a gong!"
         end
      end
   end


   class Bumpy < Adjective
      description "is bumpy"
   end

   adjective "Grumpy" do 
      description "is grumpy";
   end

   class Container < Adjective
      attr_accessor :contents
      def initialize
         @contents = [];
      end

      def +(o)
         @contents << o
         o.parent = noun;
      end

      def <<(o)
         @contents << o
         o.parent = noun;
      end

      def describe()
         "contains " + @contents.values.reduce(""){ |p,x| p + x.name }
      end

      upon :add do |added|
         
      end
   end
end

class Noun
   def bash(who)
      do "bash", who
   end
end
